"""
Tests for Zibal payment gateway client.
"""
import pytest
from unittest.mock import Mock, patch
import requests

from apps.billing.payments.zibal_client import (
    ZibalClient,
    ZibalError,
    ZibalConfig,
)


class TestZibalConfig:
    """Tests for Zibal configuration."""
    
    @patch('apps.billing.payments.zibal_client.settings')
    def test_config_defaults(self, mock_settings):
        """Test default configuration values."""
        mock_settings.ZIBAL_MERCHANT_ID = 'zibal'
        mock_settings.ZIBAL_SANDBOX = True
        
        config = ZibalConfig()
        
        assert config.merchant_id == 'zibal'
        assert config.sandbox is True
        assert config.gateway_base == 'https://gateway.zibal.ir'
    
    @patch('apps.billing.payments.zibal_client.settings')
    def test_config_sandbox_enforcement(self, mock_settings):
        """Test that sandbox enforces 'zibal' merchant."""
        mock_settings.ZIBAL_MERCHANT_ID = 'custom_merchant'
        mock_settings.ZIBAL_SANDBOX = True
        
        config = ZibalConfig()
        
        assert config.merchant_id == 'zibal'


class TestZibalClient:
    """Tests for Zibal client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = ZibalClient()
        
        assert client.config is not None
        assert client.session is not None
    
    @patch('apps.billing.payments.zibal_client.requests.Session.post')
    def test_request_payment_success(self, mock_post):
        """Test successful payment request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'trackId': 123456789,
            'result': 100,
            'message': 'success'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = ZibalClient()
        result = client.request_payment(
            amount=100000,
            order_id='TEST-001',
            callback_url='https://example.com/callback',
            mobile='09123456789'
        )
        
        assert result['success'] is True
        assert result['track_id'] == 123456789
        assert result['result'] == 100
        
        # Verify API was called with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['amount'] == 100000
        assert call_args[1]['json']['orderId'] == 'TEST-001'
        assert call_args[1]['json']['mobile'] == '09123456789'
    
    def test_request_payment_invalid_amount(self):
        """Test payment request with invalid amount."""
        client = ZibalClient()
        
        with pytest.raises(ZibalError, match='at least 1000'):
            client.request_payment(
                amount=500,  # Too low
                order_id='TEST-001',
                callback_url='https://example.com/callback'
            )
    
    @patch('apps.billing.payments.zibal_client.requests.Session.post')
    def test_request_payment_timeout(self, mock_post):
        """Test payment request timeout."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        client = ZibalClient()
        
        with pytest.raises(ZibalError, match='timeout'):
            client.request_payment(
                amount=100000,
                order_id='TEST-001',
                callback_url='https://example.com/callback'
            )
    
    def test_create_start_url(self):
        """Test creating payment start URL."""
        client = ZibalClient()
        
        url = client.create_start_url(123456789)
        
        assert url == 'https://gateway.zibal.ir/start/123456789'
    
    @patch('apps.billing.payments.zibal_client.requests.Session.post')
    def test_verify_payment_success(self, mock_post):
        """Test successful payment verification."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': 100,
            'paidAt': '2025-10-05 12:30:45',
            'amount': 100000,
            'status': 1,
            'refNumber': 987654321,
            'cardNumber': '6219-86**-****-1234',
            'message': 'success'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = ZibalClient()
        result = client.verify_payment(123456789)
        
        assert result['success'] is True
        assert result['result'] == 100
        assert result['amount'] == 100000
        assert result['ref_number'] == '987654321'
        assert result['card_number'] == '6219-86**-****-1234'
        assert result['is_duplicate'] is False
    
    @patch('apps.billing.payments.zibal_client.requests.Session.post')
    def test_verify_payment_duplicate(self, mock_post):
        """Test verification of already-verified payment."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': 201,  # Already verified
            'paidAt': '2025-10-05 12:30:45',
            'amount': 100000,
            'status': 1,
            'refNumber': 987654321,
            'cardNumber': '6219-86**-****-1234',
            'message': 'already verified'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = ZibalClient()
        result = client.verify_payment(123456789)
        
        assert result['success'] is True
        assert result['is_duplicate'] is True
    
    @patch('apps.billing.payments.zibal_client.requests.Session.post')
    def test_inquiry(self, mock_post):
        """Test payment inquiry."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': 100,
            'status': 1,
            'message': 'paid'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = ZibalClient()
        result = client.inquiry(123456789)
        
        assert result['result'] == 100
        assert result['status'] == 1
    
    def test_get_result_message(self):
        """Test getting Persian message for result codes."""
        assert 'موفقیت' in ZibalClient.get_result_message(100)
        assert 'یافت نشد' in ZibalClient.get_result_message(102)
        assert 'قبلاً تایید' in ZibalClient.get_result_message(201)
        assert 'ناشناخته' in ZibalClient.get_result_message(9999)
