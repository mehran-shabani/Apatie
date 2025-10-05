"""
Billing serializers.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Subscription, PaymentTransaction
from .payments.utils import calculate_subscription_amount, format_amount_display


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    is_active = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = (
            'id', 'plan_type', 'status', 'amount_paid', 'amount_display',
            'duration_months', 'starts_at', 'expires_at', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')
    
    def get_is_active(self, obj):
        """Check if subscription is active."""
        return obj.is_active()
    
    def get_amount_display(self, obj):
        """Get formatted amount display."""
        return format_amount_display(obj.amount_paid)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PaymentTransaction model."""
    
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = (
            'id', 'order_id', 'gateway', 'purpose', 'purpose_display',
            'amount_irr', 'amount_display', 'status', 'status_display',
            'track_id', 'result_code', 'message', 'paid_at',
            'card_pan_masked', 'ref_number', 'created_at'
        )
        read_only_fields = ('id', 'order_id', 'track_id', 'created_at')
    
    def get_amount_display(self, obj):
        """Get formatted amount display."""
        return format_amount_display(obj.amount_irr)


class SubscriptionStartRequestSerializer(serializers.Serializer):
    """Serializer for starting subscription payment."""
    
    plan_type = serializers.ChoiceField(
        choices=Subscription.PlanType.choices,
        default=Subscription.PlanType.BUSINESS,
        help_text=_('Subscription plan type')
    )
    months = serializers.IntegerField(
        min_value=1,
        max_value=24,
        default=1,
        help_text=_('Subscription duration in months')
    )
    vendor_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text=_('Vendor ID for business subscription (optional)')
    )
    
    def validate_months(self, value):
        """Validate subscription duration."""
        if value < 1:
            raise serializers.ValidationError(_('Duration must be at least 1 month'))
        if value > 24:
            raise serializers.ValidationError(_('Duration cannot exceed 24 months'))
        return value
    
    def validate(self, attrs):
        """Validate subscription request."""
        plan_type = attrs.get('plan_type')
        
        # Add business logic validation here
        # e.g., check if user is eligible for the plan
        
        return attrs


class PaymentStartResponseSerializer(serializers.Serializer):
    """Serializer for payment start response."""
    
    order_id = serializers.CharField(help_text=_('Unique order ID'))
    track_id = serializers.IntegerField(help_text=_('Payment tracking ID'))
    redirect_url = serializers.URLField(help_text=_('URL to redirect user for payment'))
    amount = serializers.IntegerField(help_text=_('Payment amount in Rials'))
    amount_display = serializers.CharField(help_text=_('Formatted amount'))
    subscription_id = serializers.IntegerField(help_text=_('Subscription ID'))


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for payment callback parameters."""
    
    trackId = serializers.IntegerField(help_text=_('Payment tracking ID'))
    success = serializers.IntegerField(required=False, help_text=_('Success indicator'))
    status = serializers.IntegerField(required=False, help_text=_('Payment status'))
    orderId = serializers.CharField(required=False, help_text=_('Order ID'))


class PaymentCallbackResponseSerializer(serializers.Serializer):
    """Serializer for payment callback response."""
    
    order_id = serializers.CharField(help_text=_('Order ID'))
    status = serializers.ChoiceField(
        choices=PaymentTransaction.PaymentStatus.choices,
        help_text=_('Transaction status')
    )
    result_code = serializers.IntegerField(
        allow_null=True,
        help_text=_('Result code from gateway')
    )
    message = serializers.CharField(
        allow_blank=True,
        help_text=_('Result message')
    )
    paid_at = serializers.DateTimeField(
        allow_null=True,
        help_text=_('Payment datetime')
    )
    subscription_id = serializers.IntegerField(
        allow_null=True,
        help_text=_('Subscription ID if applicable')
    )
