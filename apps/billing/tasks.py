"""
Celery tasks for billing app.
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import PaymentTransaction
from .payments.zibal_client import get_zibal_client, ZibalError

logger = logging.getLogger(__name__)


@shared_task
def reconcile_pending_payments():
    """
    Reconcile pending payment transactions.
    
    This task runs periodically via Celery Beat to check status
    of pending payments and update them accordingly.
    """
    logger.info('Starting payment reconciliation task')
    
    # Get pending transactions from last 24 hours
    time_threshold = timezone.now() - timedelta(hours=24)
    
    pending_transactions = PaymentTransaction.objects.filter(
        gateway=PaymentTransaction.PaymentGateway.ZIBAL,
        status__in=[
            PaymentTransaction.PaymentStatus.INITIATED,
            PaymentTransaction.PaymentStatus.PENDING
        ],
        created_at__gte=time_threshold,
        track_id__isnull=False
    ).order_by('created_at')
    
    total = pending_transactions.count()
    logger.info(f'Found {total} pending transactions to reconcile')
    
    if total == 0:
        return {'status': 'success', 'reconciled': 0, 'total': 0}
    
    zibal_client = get_zibal_client()
    
    reconciled = 0
    failed = 0
    
    for txn in pending_transactions:
        try:
            # Inquiry payment status
            inquiry_result = zibal_client.inquiry(txn.track_id)
            
            status_code = inquiry_result.get('status')
            
            with transaction.atomic():
                txn.refresh_from_db()
                
                # Skip if already processed
                if txn.status == PaymentTransaction.PaymentStatus.PAID:
                    continue
                
                # Status 1 = Paid
                if status_code == 1:
                    verify_result = zibal_client.verify_payment(txn.track_id)
                    
                    if verify_result['success']:
                        txn.mark_as_paid(
                            result_code=verify_result['result'],
                            ref_number=verify_result['ref_number'],
                            card_pan=verify_result['card_number']
                        )
                        
                        # Activate subscription if applicable
                        if txn.purpose == PaymentTransaction.PaymentPurpose.SUBSCRIPTION:
                            from .models import Subscription
                            subscription_id = txn.meta.get('subscription_id')
                            if subscription_id:
                                try:
                                    subscription = Subscription.objects.get(id=subscription_id)
                                    subscription.payment_transaction = txn
                                    subscription.amount_paid = txn.amount_irr
                                    subscription.activate(duration_months=txn.meta.get('months', 1))
                                    logger.info(f'Subscription {subscription.id} activated via reconciliation')
                                except Subscription.DoesNotExist:
                                    logger.warning(f'Subscription {subscription_id} not found')
                        
                        reconciled += 1
                        logger.info(f'Payment {txn.order_id} reconciled as PAID')
                
                # Status -2 = Cancelled
                elif status_code == -2:
                    txn.mark_as_failed(message='Payment cancelled')
                    reconciled += 1
                    logger.info(f'Payment {txn.order_id} reconciled as FAILED')
                
                # Still pending but old
                elif status_code == -1:
                    age = timezone.now() - txn.created_at
                    if age > timedelta(minutes=30):
                        txn.status = PaymentTransaction.PaymentStatus.EXPIRED
                        txn.message = 'Payment expired'
                        txn.save()
                        reconciled += 1
                        logger.info(f'Payment {txn.order_id} marked as EXPIRED')
        
        except ZibalError as e:
            logger.error(f'Reconciliation error for {txn.order_id}: {str(e)}')
            failed += 1
        except Exception as e:
            logger.error(f'Unexpected reconciliation error for {txn.order_id}: {str(e)}', exc_info=True)
            failed += 1
    
    logger.info(f'Reconciliation complete: {reconciled} reconciled, {failed} failed')
    
    return {
        'status': 'success',
        'total': total,
        'reconciled': reconciled,
        'failed': failed
    }


@shared_task
def check_expired_subscriptions():
    """
    Check and mark expired subscriptions.
    
    Runs daily to update subscription statuses.
    """
    from .models import Subscription
    
    logger.info('Starting expired subscription check')
    
    # Find active subscriptions that have expired
    expired = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE,
        expires_at__lt=timezone.now()
    )
    
    count = expired.count()
    
    if count > 0:
        expired.update(status=Subscription.SubscriptionStatus.EXPIRED)
        logger.info(f'Marked {count} subscriptions as expired')
    
    return {'status': 'success', 'expired': count}


@shared_task
def send_subscription_expiry_reminders():
    """
    Send reminders for subscriptions expiring soon.
    
    Sends notifications 7 days and 1 day before expiry.
    """
    from .models import Subscription
    
    logger.info('Starting subscription expiry reminders')
    
    now = timezone.now()
    seven_days = now + timedelta(days=7)
    one_day = now + timedelta(days=1)
    
    # Find subscriptions expiring in 7 days
    expiring_soon = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE,
        expires_at__range=(now, seven_days)
    ).select_related('user')
    
    reminded = 0
    
    for subscription in expiring_soon:
        # TODO: Send notification via SMS or push
        # For now just log
        days_left = (subscription.expires_at - now).days
        logger.info(
            f'Subscription {subscription.id} expires in {days_left} days',
            extra={
                'user_id': subscription.user.id,
                'subscription_id': subscription.id,
                'expires_at': subscription.expires_at
            }
        )
        reminded += 1
    
    return {'status': 'success', 'reminded': reminded}
