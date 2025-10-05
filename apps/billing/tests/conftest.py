"""
Pytest fixtures for billing tests.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(
        mobile='09123456789',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def vendor(db, user):
    """Create test vendor."""
    from apps.vendors.models import Vendor
    
    vendor_user = User.objects.create_user(
        mobile='09198765432',
        password='testpass123',
        user_type=User.UserType.VENDOR
    )
    
    return Vendor.objects.create(
        user=vendor_user,
        name='Test Clinic',
        vendor_type=Vendor.VendorType.DOCTOR,
        is_verified=True,
        is_active=True
    )


@pytest.fixture
def zibal_mock():
    """Mock Zibal client responses."""
    class ZibalMock:
        def __init__(self):
            self.request_payment = Mock(return_value={
                'track_id': 123456789,
                'result': 100,
                'message': 'success',
                'success': True
            })
            
            self.verify_payment = Mock(return_value={
                'result': 100,
                'paid_at': '2025-10-05 12:30:45',
                'amount': 500000,
                'ref_number': '987654321',
                'card_number': '6219-86**-****-1234',
                'status': 1,
                'order_id': 'AP-20251005123000-1-abc123',
                'message': 'success',
                'success': True,
                'is_duplicate': False
            })
            
            self.inquiry = Mock(return_value={
                'result': 100,
                'status': 1,
                'message': 'paid'
            })
            
            self.create_start_url = Mock(return_value='https://gateway.zibal.ir/start/123456789')
    
    with patch('apps.billing.payments.zibal_client.get_zibal_client') as mock_client:
        mock_client.return_value = ZibalMock()
        yield mock_client.return_value


@pytest.fixture
def zibal_mock_failed():
    """Mock Zibal client with failed payment."""
    class ZibalMockFailed:
        def __init__(self):
            self.request_payment = Mock(return_value={
                'track_id': 123456789,
                'result': 100,
                'message': 'success',
                'success': True
            })
            
            self.verify_payment = Mock(return_value={
                'result': 202,
                'paid_at': '',
                'amount': 500000,
                'ref_number': '',
                'card_number': '',
                'status': -2,
                'order_id': 'AP-20251005123000-1-abc123',
                'message': 'cancelled',
                'success': False,
                'is_duplicate': False
            })
            
            self.create_start_url = Mock(return_value='https://gateway.zibal.ir/start/123456789')
    
    with patch('apps.billing.payments.zibal_client.get_zibal_client') as mock_client:
        mock_client.return_value = ZibalMockFailed()
        yield mock_client.return_value


@pytest.fixture
def zibal_mock_duplicate():
    """Mock Zibal client with duplicate payment."""
    class ZibalMockDuplicate:
        def __init__(self):
            self.verify_payment = Mock(return_value={
                'result': 201,
                'paid_at': '2025-10-05 12:30:45',
                'amount': 500000,
                'ref_number': '987654321',
                'card_number': '6219-86**-****-1234',
                'status': 1,
                'order_id': 'AP-20251005123000-1-abc123',
                'message': 'already verified',
                'success': True,
                'is_duplicate': True
            })
    
    with patch('apps.billing.payments.zibal_client.get_zibal_client') as mock_client:
        mock_client.return_value = ZibalMockDuplicate()
        yield mock_client.return_value
