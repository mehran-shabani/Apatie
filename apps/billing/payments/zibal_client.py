"""
Zibal payment gateway client.

Documentation: https://docs.zibal.ir
"""
import logging
from typing import Dict, Optional, Any
from decimal import Decimal

import requests
from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class ZibalConfig:
    """Zibal configuration."""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'ZIBAL_MERCHANT_ID', 'zibal')
        self.gateway_base = getattr(settings, 'ZIBAL_GATEWAY_BASE', 'https://gateway.zibal.ir')
        self.api_base = getattr(settings, 'ZIBAL_API_BASE', 'https://gateway.zibal.ir')
        self.timeout = getattr(settings, 'ZIBAL_TIMEOUT', 10)
        self.sandbox = getattr(settings, 'ZIBAL_SANDBOX', True)
        
        # For dev/test, use 'zibal' as merchant
        if self.sandbox and self.merchant_id != 'zibal':
            logger.warning("Sandbox mode enabled but merchant is not 'zibal'. Using 'zibal' for testing.")
            self.merchant_id = 'zibal'


class ZibalRequestResponse(BaseModel):
    """Response model for payment request."""
    trackId: int = Field(..., description="Tracking ID from Zibal")
    result: int = Field(..., description="Result code (100 = success)")
    message: str = Field(default="", description="Response message")


class ZibalVerifyResponse(BaseModel):
    """Response model for payment verification."""
    paidAt: str = Field(default="", description="Payment datetime")
    amount: int = Field(..., description="Amount in Rials")
    result: int = Field(..., description="Result code (100 = success)")
    status: int = Field(..., description="Payment status")
    refNumber: Optional[int] = Field(None, description="Reference number")
    description: Optional[str] = Field(None, description="Payment description")
    cardNumber: Optional[str] = Field(None, description="Masked card number")
    orderId: Optional[str] = Field(None, description="Order ID")
    message: str = Field(default="", description="Response message")


class ZibalError(Exception):
    """Base exception for Zibal errors."""
    pass


class ZibalClient:
    """
    Zibal payment gateway client.
    
    Handles payment request, verification, and inquiry operations.
    """
    
    # Zibal result codes
    RESULT_SUCCESS = 100
    RESULT_ALREADY_PAID = 201
    RESULT_PAYMENT_NOT_FOUND = 102
    
    # Status codes
    STATUS_PAID = 1
    STATUS_PENDING = -1
    STATUS_CANCELLED = -2
    
    def __init__(self):
        self.config = ZibalConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to Zibal API with retry logic.
        
        Args:
            endpoint: API endpoint path
            data: Request payload
            
        Returns:
            Response JSON data
            
        Raises:
            ZibalError: If request fails
        """
        url = f"{self.config.api_base}/{endpoint}"
        
        logger.info(f"Zibal request to {endpoint}", extra={
            'endpoint': endpoint,
            'merchant': self.config.merchant_id,
            'sandbox': self.config.sandbox
        })
        
        try:
            response = self.session.post(
                url,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Zibal response from {endpoint}", extra={
                'endpoint': endpoint,
                'result': result.get('result'),
                'message': result.get('message', '')
            })
            
            return result
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Zibal timeout on {endpoint}", exc_info=True)
            raise ZibalError(f"Gateway timeout: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Zibal request error on {endpoint}", exc_info=True)
            raise ZibalError(f"Gateway error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error on {endpoint}", exc_info=True)
            raise ZibalError(f"Unexpected error: {str(e)}")
    
    def request_payment(
        self,
        amount: int,
        order_id: str,
        callback_url: str,
        mobile: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Request a new payment from Zibal.
        
        Args:
            amount: Amount in Rials (must be at least 1000)
            order_id: Unique order identifier for idempotency
            callback_url: URL to redirect after payment
            mobile: User mobile number (optional)
            description: Payment description (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - track_id: Tracking ID for the payment
                - result: Result code (100 = success)
                - message: Response message
                
        Raises:
            ZibalError: If request fails
        """
        if amount < 1000:
            raise ZibalError("Amount must be at least 1000 Rials")
        
        payload = {
            'merchant': self.config.merchant_id,
            'amount': amount,
            'orderId': order_id,
            'callbackUrl': callback_url,
        }
        
        if mobile:
            payload['mobile'] = mobile
        if description:
            payload['description'] = description
        
        # Add optional fields
        payload.update(kwargs)
        
        try:
            result = self._make_request('v1/request', payload)
            
            # Validate response
            validated = ZibalRequestResponse(**result)
            
            return {
                'track_id': validated.trackId,
                'result': validated.result,
                'message': validated.message,
                'success': validated.result == self.RESULT_SUCCESS
            }
            
        except ValidationError as e:
            logger.error("Invalid Zibal response format", exc_info=True)
            raise ZibalError(f"Invalid response: {str(e)}")
    
    def create_start_url(self, track_id: int) -> str:
        """
        Create payment start URL for redirecting user to gateway.
        
        Args:
            track_id: Tracking ID from request_payment
            
        Returns:
            Full URL to redirect user to
        """
        return f"{self.config.gateway_base}/start/{track_id}"
    
    def verify_payment(self, track_id: int) -> Dict[str, Any]:
        """
        Verify a payment with Zibal.
        
        This MUST be called after receiving callback to confirm payment.
        Only the verify response is trustworthy.
        
        Args:
            track_id: Tracking ID of the payment
            
        Returns:
            Dictionary with:
                - result: Result code (100 = success, 201 = already verified)
                - paid_at: Payment datetime string
                - amount: Amount in Rials
                - ref_number: Reference number
                - card_number: Masked card number
                - status: Payment status
                - message: Response message
                
        Raises:
            ZibalError: If verification fails
        """
        payload = {
            'merchant': self.config.merchant_id,
            'trackId': track_id,
        }
        
        try:
            result = self._make_request('v1/verify', payload)
            
            # Validate response
            validated = ZibalVerifyResponse(**result)
            
            return {
                'result': validated.result,
                'paid_at': validated.paidAt,
                'amount': validated.amount,
                'ref_number': str(validated.refNumber) if validated.refNumber else '',
                'card_number': validated.cardNumber or '',
                'status': validated.status,
                'order_id': validated.orderId or '',
                'message': validated.message,
                'success': validated.result in [self.RESULT_SUCCESS, self.RESULT_ALREADY_PAID],
                'is_duplicate': validated.result == self.RESULT_ALREADY_PAID
            }
            
        except ValidationError as e:
            logger.error("Invalid verify response format", exc_info=True)
            raise ZibalError(f"Invalid verify response: {str(e)}")
    
    def inquiry(self, track_id: int) -> Dict[str, Any]:
        """
        Inquiry about a payment status (for reconciliation).
        
        Similar to verify but doesn't finalize the payment.
        
        Args:
            track_id: Tracking ID of the payment
            
        Returns:
            Payment status information
            
        Raises:
            ZibalError: If inquiry fails
        """
        payload = {
            'merchant': self.config.merchant_id,
            'trackId': track_id,
        }
        
        try:
            result = self._make_request('v1/inquiry', payload)
            return result
        except Exception as e:
            logger.error(f"Inquiry failed for track_id {track_id}", exc_info=True)
            raise ZibalError(f"Inquiry failed: {str(e)}")
    
    @staticmethod
    def get_result_message(result_code: int) -> str:
        """
        Get Persian message for Zibal result code.
        
        Args:
            result_code: Zibal result code
            
        Returns:
            Persian message describing the result
        """
        messages = {
            100: "پرداخت با موفقیت انجام شد",
            102: "تراکنش یافت نشد",
            103: "مرچنت نامعتبر است",
            104: "مرچنت غیرفعال است",
            105: "مبلغ نامعتبر است",
            106: "تراکنش قبلاً وریفای شده است",
            113: "مبلغ بیش از سقف مجاز است",
            201: "قبلاً تایید شده",
            202: "سفارش پرداخت نشده یا ناموفق بوده است",
            203: "trackId نامعتبر است",
        }
        return messages.get(result_code, f"کد خطای ناشناخته: {result_code}")


# Singleton instance
_client_instance = None


def get_zibal_client() -> ZibalClient:
    """Get or create Zibal client singleton."""
    global _client_instance
    if _client_instance is None:
        _client_instance = ZibalClient()
    return _client_instance
