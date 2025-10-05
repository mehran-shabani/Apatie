"""
Billing models for Apatye project.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Subscription(TimeStampedModel):
    """
    Business Plan Boost subscription model.
    """
    class PlanType(models.TextChoices):
        BUSINESS = 'business', _('Business Plan')
        # Future: Add more plan types if needed

    class SubscriptionStatus(models.TextChoices):
        PENDING = 'pending', _('Pending Payment')
        ACTIVE = 'active', _('Active')
        EXPIRED = 'expired', _('Expired')
        CANCELLED = 'cancelled', _('Cancelled')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('User')
    )
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('Vendor'),
        null=True,
        blank=True,
        help_text=_('Vendor associated with this subscription')
    )
    
    plan_type = models.CharField(
        _('Plan type'),
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.BUSINESS
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.PENDING
    )
    
    amount_paid = models.PositiveIntegerField(_('Amount paid (IRR)'), default=0)
    duration_months = models.PositiveSmallIntegerField(_('Duration (months)'), default=1)
    
    starts_at = models.DateTimeField(_('Starts at'), null=True, blank=True)
    expires_at = models.DateTimeField(_('Expires at'), null=True, blank=True)
    
    payment_transaction = models.ForeignKey(
        'PaymentTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
        verbose_name=_('Payment transaction')
    )
    
    notes = models.TextField(_('Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        db_table = 'billing_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.mobile} - {self.plan_type} ({self.status})'

    def is_active(self):
        """Check if subscription is currently active."""
        if self.status != self.SubscriptionStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def activate(self, duration_months=None):
        """Activate subscription and set expiry date."""
        if duration_months:
            self.duration_months = duration_months
        
        now = timezone.now()
        self.status = self.SubscriptionStatus.ACTIVE
        self.starts_at = now
        
        # Calculate expiry date
        from dateutil.relativedelta import relativedelta
        self.expires_at = now + relativedelta(months=self.duration_months)
        self.save()

    def extend(self, months):
        """Extend subscription duration."""
        from dateutil.relativedelta import relativedelta
        
        if self.expires_at and self.expires_at > timezone.now():
            # Extend from current expiry
            self.expires_at = self.expires_at + relativedelta(months=months)
        else:
            # Restart from now
            now = timezone.now()
            self.starts_at = now
            self.expires_at = now + relativedelta(months=months)
            self.status = self.SubscriptionStatus.ACTIVE
        
        self.save()


class PaymentTransaction(TimeStampedModel):
    """
    Payment transaction model for tracking all payments through payment gateways.
    """
    class PaymentPurpose(models.TextChoices):
        SUBSCRIPTION = 'subscription', _('Subscription')
        APPOINTMENT_DEPOSIT = 'appointment_deposit', _('Appointment Deposit')
        DELIVERY_FEE = 'delivery_fee', _('Delivery Fee')

    class PaymentGateway(models.TextChoices):
        ZIBAL = 'zibal', _('Zibal')
        # Future: Add more gateways

    class PaymentStatus(models.TextChoices):
        INITIATED = 'initiated', _('Initiated')
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        EXPIRED = 'expired', _('Expired')
        REFUNDED = 'refunded', _('Refunded')

    # Core fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        verbose_name=_('User')
    )
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_transactions',
        verbose_name=_('Vendor'),
        help_text=_('Vendor receiving the payment (for subscriptions)')
    )
    
    purpose = models.CharField(
        _('Purpose'),
        max_length=30,
        choices=PaymentPurpose.choices,
        default=PaymentPurpose.SUBSCRIPTION
    )
    amount_irr = models.PositiveIntegerField(_('Amount (IRR)'))
    
    # Idempotency & Gateway
    order_id = models.CharField(
        _('Order ID'),
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_('Unique order ID for idempotency')
    )
    gateway = models.CharField(
        _('Gateway'),
        max_length=20,
        choices=PaymentGateway.choices,
        default=PaymentGateway.ZIBAL
    )
    
    # Gateway-specific fields
    track_id = models.BigIntegerField(
        _('Track ID'),
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Gateway tracking ID')
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.INITIATED
    )
    
    # Result fields
    result_code = models.IntegerField(_('Result code'), null=True, blank=True)
    message = models.CharField(_('Message'), max_length=500, blank=True)
    
    # Payment details
    paid_at = models.DateTimeField(_('Paid at'), null=True, blank=True)
    card_pan_masked = models.CharField(_('Card PAN (masked)'), max_length=20, blank=True)
    ref_number = models.CharField(_('Reference number'), max_length=100, blank=True)
    
    # Metadata
    meta = models.JSONField(_('Metadata'), default=dict, blank=True)
    callback_url = models.URLField(_('Callback URL'), max_length=500, blank=True)
    
    class Meta:
        verbose_name = _('Payment Transaction')
        verbose_name_plural = _('Payment Transactions')
        db_table = 'billing_payment_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gateway', 'order_id']),
            models.Index(fields=['gateway', 'track_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['gateway', 'track_id'],
                name='unique_gateway_track_id',
                condition=models.Q(track_id__isnull=False)
            )
        ]

    def __str__(self):
        return f'{self.order_id} - {self.gateway} - {self.status} - {self.amount_irr} IRR'

    def mark_as_paid(self, result_code=None, ref_number='', card_pan=''):
        """Mark transaction as paid."""
        self.status = self.PaymentStatus.PAID
        self.paid_at = timezone.now()
        self.result_code = result_code
        self.ref_number = ref_number
        self.card_pan_masked = card_pan
        self.save()

    def mark_as_failed(self, result_code=None, message=''):
        """Mark transaction as failed."""
        self.status = self.PaymentStatus.FAILED
        self.result_code = result_code
        self.message = message
        self.save()

    def is_pending(self):
        """Check if transaction is pending."""
        return self.status in [
            self.PaymentStatus.INITIATED,
            self.PaymentStatus.PENDING
        ]

    def is_successful(self):
        """Check if transaction was successful."""
        return self.status == self.PaymentStatus.PAID
