"""
Billing views and API endpoints.
"""
import logging
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Subscription, PaymentTransaction
from .serializers import (
    SubscriptionSerializer,
    PaymentTransactionSerializer,
    SubscriptionStartRequestSerializer,
    PaymentStartResponseSerializer,
    PaymentCallbackSerializer,
    PaymentCallbackResponseSerializer,
)
from .payments.zibal_client import get_zibal_client, ZibalError
from .payments.utils import generate_order_id, calculate_subscription_amount, format_amount_display

logger = logging.getLogger(__name__)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get subscriptions for current user."""
        return Subscription.objects.filter(user=self.request.user).select_related(
            'payment_transaction', 'vendor'
        )
    
    @extend_schema(
        summary="Get current user's active subscriptions",
        description="Returns all active subscriptions for the authenticated user."
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's subscriptions."""
        subscriptions = self.get_queryset().filter(
            status=Subscription.SubscriptionStatus.ACTIVE
        )
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=SubscriptionStartRequestSerializer,
        responses={201: PaymentStartResponseSerializer},
        summary="Start subscription payment",
        description=(
            "Initiates a new subscription payment process. "
            "Creates a payment transaction and returns redirect URL to payment gateway."
        )
    )
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start subscription payment process.
        
        Creates a PaymentTransaction and returns redirect URL to gateway.
        """
        serializer = SubscriptionStartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_type = serializer.validated_data['plan_type']
        months = serializer.validated_data['months']
        vendor_id = serializer.validated_data.get('vendor_id')
        
        # Calculate amount
        amount = calculate_subscription_amount(months)
        
        # Validate vendor if provided
        vendor = None
        if vendor_id:
            from apps.vendors.models import Vendor
            vendor = get_object_or_404(Vendor, id=vendor_id, is_active=True)
        
        try:
            with transaction.atomic():
                # Generate unique order ID
                order_id = generate_order_id(user_id=request.user.id)
                
                # Create subscription (pending payment)
                subscription = Subscription.objects.create(
                    user=request.user,
                    vendor=vendor,
                    plan_type=plan_type,
                    status=Subscription.SubscriptionStatus.PENDING,
                    amount_paid=0,
                    duration_months=months
                )
                
                # Build callback URL
                callback_url = request.build_absolute_uri('/api/payments/zibal/callback/')
                
                # Create payment transaction
                payment = PaymentTransaction.objects.create(
                    user=request.user,
                    vendor=vendor,
                    purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
                    amount_irr=amount,
                    order_id=order_id,
                    gateway=PaymentTransaction.PaymentGateway.ZIBAL,
                    status=PaymentTransaction.PaymentStatus.INITIATED,
                    callback_url=callback_url,
                    meta={
                        'subscription_id': subscription.id,
                        'plan_type': plan_type,
                        'months': months,
                    }
                )
                
                # Request payment from Zibal
                zibal_client = get_zibal_client()
                
                try:
                    result = zibal_client.request_payment(
                        amount=amount,
                        order_id=order_id,
                        callback_url=callback_url,
                        mobile=request.user.mobile,
                        description=f"اشتراک {months} ماهه {subscription.get_plan_type_display()}"
                    )
                    
                    if not result['success']:
                        raise ZibalError(f"Payment request failed: {result.get('message')}")
                    
                    # Update payment with track_id
                    payment.track_id = result['track_id']
                    payment.status = PaymentTransaction.PaymentStatus.PENDING
                    payment.save()
                    
                    # Create redirect URL
                    redirect_url = zibal_client.create_start_url(result['track_id'])
                    
                    logger.info(
                        f"Payment started: order_id={order_id}, track_id={result['track_id']}",
                        extra={
                            'user_id': request.user.id,
                            'order_id': order_id,
                            'track_id': result['track_id'],
                            'amount': amount
                        }
                    )
                    
                    response_data = {
                        'order_id': order_id,
                        'track_id': result['track_id'],
                        'redirect_url': redirect_url,
                        'amount': amount,
                        'amount_display': format_amount_display(amount),
                        'subscription_id': subscription.id,
                    }
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except ZibalError as e:
                    logger.error(f"Zibal error: {str(e)}", exc_info=True)
                    payment.mark_as_failed(message=str(e))
                    return Response(
                        {'error': f'خطا در اتصال به درگاه پرداخت: {str(e)}'},
                        status=status.HTTP_502_BAD_GATEWAY
                    )
                    
        except Exception as e:
            logger.error(f"Unexpected error in payment start: {str(e)}", exc_info=True)
            return Response(
                {'error': 'خطای داخلی سرور'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentCallbackView(views.APIView):
    """
    Payment gateway callback view.
    
    Handles callbacks from Zibal after user completes/cancels payment.
    """
    permission_classes = [AllowAny]  # Gateway doesn't authenticate
    
    @extend_schema(
        parameters=[
            OpenApiParameter('trackId', int, description='Payment tracking ID'),
            OpenApiParameter('success', int, description='Success indicator', required=False),
            OpenApiParameter('status', int, description='Payment status', required=False),
            OpenApiParameter('orderId', str, description='Order ID', required=False),
        ],
        responses={200: PaymentCallbackResponseSerializer},
        summary="Payment gateway callback",
        description=(
            "Called by payment gateway after user completes/cancels payment. "
            "Verifies payment and updates transaction status."
        )
    )
    def get(self, request):
        """Handle GET callback from Zibal."""
        return self._handle_callback(request)
    
    def post(self, request):
        """Handle POST callback from Zibal."""
        return self._handle_callback(request)
    
    def _handle_callback(self, request):
        """
        Handle payment callback (GET or POST).
        
        This is the critical path where payment is verified.
        Only trust the verify response, not callback parameters.
        """
        serializer = PaymentCallbackSerializer(data=request.query_params or request.data)
        serializer.is_valid(raise_exception=True)
        
        track_id = serializer.validated_data['trackId']
        
        logger.info(
            f"Payment callback received: track_id={track_id}",
            extra={'track_id': track_id}
        )
        
        try:
            # Find transaction by track_id
            payment = PaymentTransaction.objects.select_for_update().get(
                track_id=track_id,
                gateway=PaymentTransaction.PaymentGateway.ZIBAL
            )
            
            # Check if already processed (idempotency)
            if payment.status == PaymentTransaction.PaymentStatus.PAID:
                logger.info(f"Payment already processed: {payment.order_id}")
                return self._build_response(payment)
            
            # Verify payment with Zibal
            zibal_client = get_zibal_client()
            
            try:
                verify_result = zibal_client.verify_payment(track_id)
                
                logger.info(
                    f"Verify result: order_id={payment.order_id}, result={verify_result['result']}",
                    extra={
                        'order_id': payment.order_id,
                        'result': verify_result['result'],
                        'amount': verify_result['amount']
                    }
                )
                
                if verify_result['success']:
                    # Payment successful
                    with transaction.atomic():
                        payment.mark_as_paid(
                            result_code=verify_result['result'],
                            ref_number=verify_result['ref_number'],
                            card_pan=verify_result['card_number']
                        )
                        
                        # Update meta with verify data
                        payment.meta.update({
                            'verified_at': verify_result['paid_at'],
                            'verify_amount': verify_result['amount'],
                        })
                        payment.save()
                        
                        # Activate subscription if this is a subscription payment
                        if payment.purpose == PaymentTransaction.PaymentPurpose.SUBSCRIPTION:
                            subscription_id = payment.meta.get('subscription_id')
                            if subscription_id:
                                try:
                                    subscription = Subscription.objects.get(id=subscription_id)
                                    subscription.payment_transaction = payment
                                    subscription.amount_paid = payment.amount_irr
                                    subscription.activate(duration_months=payment.meta.get('months', 1))
                                    
                                    logger.info(
                                        f"Subscription activated: {subscription.id}",
                                        extra={'subscription_id': subscription.id}
                                    )
                                except Subscription.DoesNotExist:
                                    logger.error(f"Subscription {subscription_id} not found")
                        
                        logger.info(f"Payment completed: {payment.order_id}")
                else:
                    # Payment failed or cancelled
                    payment.mark_as_failed(
                        result_code=verify_result['result'],
                        message=verify_result.get('message', 'پرداخت ناموفق')
                    )
                    logger.warning(f"Payment failed: {payment.order_id}")
                
                return self._build_response(payment)
                
            except ZibalError as e:
                logger.error(f"Zibal verify error: {str(e)}", exc_info=True)
                payment.mark_as_failed(message=f"خطای تأیید پرداخت: {str(e)}")
                return self._build_response(payment)
                
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Payment transaction not found for track_id: {track_id}")
            return Response(
                {'error': 'تراکنش یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error in callback: {str(e)}", exc_info=True)
            return Response(
                {'error': 'خطای داخلی سرور'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_response(self, payment: PaymentTransaction):
        """Build callback response data."""
        response_data = {
            'order_id': payment.order_id,
            'status': payment.status,
            'result_code': payment.result_code,
            'message': payment.message or zibal_client.get_result_message(payment.result_code or 0),
            'paid_at': payment.paid_at,
            'subscription_id': payment.meta.get('subscription_id'),
        }
        
        # Redirect to frontend success/failure page
        # You can customize this based on your frontend URLs
        if payment.status == PaymentTransaction.PaymentStatus.PAID:
            frontend_url = f"{settings.ZIBAL_CALLBACK_BASE}/payment/success?order_id={payment.order_id}"
        else:
            frontend_url = f"{settings.ZIBAL_CALLBACK_BASE}/payment/failed?order_id={payment.order_id}"
        
        response_data['redirect'] = frontend_url
        
        return Response(response_data, status=status.HTTP_200_OK)


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payment transactions.
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get transactions for current user."""
        return PaymentTransaction.objects.filter(user=self.request.user).select_related('vendor')
    
    @extend_schema(
        summary="Get transaction by order ID",
        description="Retrieve payment transaction details by order ID."
    )
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>[^/.]+)')
    def by_order_id(self, request, order_id=None):
        """Get transaction by order ID."""
        transaction = get_object_or_404(
            self.get_queryset(),
            order_id=order_id
        )
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)
