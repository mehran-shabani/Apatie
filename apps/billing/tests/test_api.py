"""
Tests for billing API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.billing.models import Subscription, PaymentTransaction


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.mark.django_db
class TestSubscriptionAPI:
    """Tests for subscription API endpoints."""
    
    def test_subscription_start_success(self, api_client, user, zibal_mock):
        """Test successful subscription payment start."""
        api_client.force_authenticate(user=user)
        
        url = reverse('subscription-start')
        data = {
            'plan_type': 'business',
            'months': 3
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_id' in response.data
        assert 'track_id' in response.data
        assert 'redirect_url' in response.data
        assert response.data['track_id'] == 123456789
        
        # Verify transaction was created
        transaction = PaymentTransaction.objects.get(order_id=response.data['order_id'])
        assert transaction.user == user
        assert transaction.status == PaymentTransaction.PaymentStatus.PENDING
        assert transaction.track_id == 123456789
        
        # Verify subscription was created
        subscription = Subscription.objects.get(id=response.data['subscription_id'])
        assert subscription.user == user
        assert subscription.status == Subscription.SubscriptionStatus.PENDING
    
    def test_subscription_start_unauthenticated(self, api_client):
        """Test subscription start without authentication."""
        url = reverse('subscription-start')
        data = {'plan_type': 'business', 'months': 1}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_subscription_start_invalid_months(self, api_client, user, zibal_mock):
        """Test subscription start with invalid duration."""
        api_client.force_authenticate(user=user)
        
        url = reverse('subscription-start')
        data = {
            'plan_type': 'business',
            'months': 0  # Invalid
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_my_subscriptions(self, api_client, user):
        """Test getting user's subscriptions."""
        api_client.force_authenticate(user=user)
        
        # Create active subscription
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.ACTIVE,
            amount_paid=500000,
            duration_months=1
        )
        subscription.activate()
        
        url = reverse('subscription-me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == subscription.id


@pytest.mark.django_db
class TestPaymentCallback:
    """Tests for payment callback endpoint."""
    
    def test_callback_success(self, api_client, user, zibal_mock):
        """Test successful payment callback."""
        # Create pending transaction
        subscription = Subscription.objects.create(
            user=user,
            plan_type=Subscription.PlanType.BUSINESS,
            status=Subscription.SubscriptionStatus.PENDING,
            amount_paid=0,
            duration_months=1
        )
        
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PENDING,
            track_id=123456789,
            meta={'subscription_id': subscription.id, 'months': 1}
        )
        
        url = reverse('zibal-callback')
        response = api_client.get(url, {'trackId': 123456789})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_id'] == transaction.order_id
        assert response.data['status'] == PaymentTransaction.PaymentStatus.PAID
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        assert transaction.status == PaymentTransaction.PaymentStatus.PAID
        assert transaction.paid_at is not None
        
        # Verify subscription was activated
        subscription.refresh_from_db()
        assert subscription.status == Subscription.SubscriptionStatus.ACTIVE
        assert subscription.is_active()
    
    def test_callback_failed_payment(self, api_client, user, zibal_mock_failed):
        """Test callback with failed payment."""
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PENDING,
            track_id=123456789
        )
        
        url = reverse('zibal-callback')
        response = api_client.get(url, {'trackId': 123456789})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PaymentTransaction.PaymentStatus.FAILED
        
        # Verify transaction was marked as failed
        transaction.refresh_from_db()
        assert transaction.status == PaymentTransaction.PaymentStatus.FAILED
    
    def test_callback_idempotency(self, api_client, user, zibal_mock_duplicate):
        """Test callback idempotency (duplicate verify call)."""
        # Create already-paid transaction
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PAID,
            track_id=123456789,
            ref_number='987654321'
        )
        
        url = reverse('zibal-callback')
        response = api_client.get(url, {'trackId': 123456789})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PaymentTransaction.PaymentStatus.PAID
        
        # Verify transaction wasn't changed
        transaction.refresh_from_db()
        assert transaction.status == PaymentTransaction.PaymentStatus.PAID
    
    def test_callback_not_found(self, api_client):
        """Test callback with non-existent track_id."""
        url = reverse('zibal-callback')
        response = api_client.get(url, {'trackId': 999999999})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPaymentTransactionAPI:
    """Tests for payment transaction API."""
    
    def test_get_transactions(self, api_client, user):
        """Test getting user's transactions."""
        api_client.force_authenticate(user=user)
        
        # Create transactions
        PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-test1',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PAID
        )
        
        url = reverse('transaction-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_get_transaction_by_order_id(self, api_client, user):
        """Test getting transaction by order ID."""
        api_client.force_authenticate(user=user)
        
        transaction = PaymentTransaction.objects.create(
            user=user,
            purpose=PaymentTransaction.PaymentPurpose.SUBSCRIPTION,
            amount_irr=500000,
            order_id='AP-20251005-1-unique',
            gateway=PaymentTransaction.PaymentGateway.ZIBAL,
            status=PaymentTransaction.PaymentStatus.PAID
        )
        
        url = reverse('transaction-by-order-id', kwargs={'order_id': transaction.order_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_id'] == transaction.order_id
