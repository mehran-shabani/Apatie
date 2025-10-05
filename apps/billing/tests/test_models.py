"""
Tests for billing models.
"""
import pytest
from datetime import timedelta
from django.utils import timezone

from apps.billing.models import Subscription, PaymentTransaction


@pytest.mark.django_db
class TestSubscription:
    """Tests for Subscription model."""
    
    def test_create_subscription(self, user):
        """Test creating a subscription."""
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.PENDING,
            amount_paid=0,
            duration_months=1
        )
        
        assert subscription.user == user
        assert subscription.plan_type == Subscription.PlanType.BUSINESS
        assert subscription.status == Subscription.SubscriptionStatus.PENDING
        assert not subscription.is_active()
    
    def test_activate_subscription(self, user):
        """Test activating a subscription."""
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.PENDING,
            amount_paid=500000,
            duration_months=1
        )
        
        subscription.activate()
        
        assert subscription.status == Subscription.SubscriptionStatus.ACTIVE
        assert subscription.starts_at is not None
        assert subscription.expires_at is not None
        assert subscription.is_active()
    
    def test_subscription_expiry(self, user):
        """Test subscription expiry check."""
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.ACTIVE,
            amount_paid=500000,
            duration_months=1,
            starts_at=timezone.now() - timedelta(days=40),
            expires_at=timezone.now() - timedelta(days=10)
        )
        
        assert not subscription.is_active()
    
    def test_extend_subscription(self, user):
        """Test extending subscription."""
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.ACTIVE,
            amount_paid=500000,
            duration_months=1
        )
        
        subscription.activate()
        old_expires_at = subscription.expires_at
        
        subscription.extend(months=2)
        
        assert subscription.expires_at > old_expires_at


@pytest.mark.django_db
class TestPaymentTransaction:
    """Tests for PaymentTransaction model."""
    
    def test_create_transaction(self, user):
        """Test creating a payment transaction."""
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.INITIATED
        )
        
        assert transaction.user == user
        assert transaction.amount_irr == 500000
        assert transaction.status == PaymentTransaction.PaymentStatus.INITIATED
        assert transaction.is_pending()
    
    def test_mark_as_paid(self, user):
        """Test marking transaction as paid."""
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PENDING,
            track_id=123456789
        )
        
        transaction.mark_as_paid(
            result_code=100,
            ref_number='987654321',
            card_pan='6219-86**-****-1234'
        )
        
        assert transaction.status == PaymentTransaction.PaymentStatus.PAID
        assert transaction.paid_at is not None
        assert transaction.ref_number == '987654321'
        assert transaction.card_pan_masked == '6219-86**-****-1234'
        assert transaction.is_successful()
    
    def test_mark_as_failed(self, user):
        """Test marking transaction as failed."""
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PENDING,
            track_id=123456789
        )
        
        transaction.mark_as_failed(
            result_code=202,
            message='Payment cancelled'
        )
        
        assert transaction.status == PaymentTransaction.PaymentStatus.FAILED
        assert transaction.result_code == 202
        assert transaction.message == 'Payment cancelled'
        assert not transaction.is_successful()
    
    def test_unique_order_id(self, user):
        """Test order_id uniqueness constraint."""
        order_id = 'AP-20251005-1-unique'
        
        PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id=order_id,
            gateway=PaymentTransaction.PaymentGateway.ZIBAL
        )
        
        with pytest.raises(Exception):  # IntegrityError
            PaymentTransaction.objects.create(
                user=user,
                purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
                amount_irr=500000,
                order_id=order_id,
                gateway=PaymentTransaction.PaymentGateway.ZIBAL
            )
