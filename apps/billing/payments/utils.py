"""
Payment utilities for order ID generation and helpers.
"""
import uuid
from datetime import datetime
from typing import Optional

from django.utils import timezone


def generate_order_id(prefix: str = 'AP', user_id: Optional[int] = None) -> str:
    """
    Generate unique order ID for payment transactions.
    
    Format: {prefix}-{timestamp}-{user_id}-{random}
    Example: AP-20251005142530-123-abc123
    
    Args:
        prefix: Order ID prefix (default: 'AP' for Apatye)
        user_id: User ID to include in order ID
        
    Returns:
        Unique order ID string
    """
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_part = uuid.uuid4().hex[:6]
    
    if user_id:
        return f"{prefix}-{timestamp}-{user_id}-{random_part}"
    else:
        return f"{prefix}-{timestamp}-{random_part}"


def format_amount_display(amount_rials: int) -> str:
    """
    Format amount in Rials for display.
    
    Args:
        amount_rials: Amount in Rials
        
    Returns:
        Formatted string with thousand separators and currency
    """
    return f"{amount_rials:,} ریال"


def calculate_subscription_amount(months: int, base_price: int = 500000) -> int:
    """
    Calculate subscription amount based on duration.
    
    Args:
        months: Number of months
        base_price: Base monthly price in Rials (default: 500,000)
        
    Returns:
        Total amount in Rials
    """
    # Apply discounts for longer periods
    if months >= 12:
        discount = 0.15  # 15% off for yearly
    elif months >= 6:
        discount = 0.10  # 10% off for 6 months
    elif months >= 3:
        discount = 0.05  # 5% off for 3 months
    else:
        discount = 0
    
    total = base_price * months
    discounted = int(total * (1 - discount))
    
    return discounted


def mask_card_number(card_number: str) -> str:
    """
    Mask credit card number for security.
    
    Args:
        card_number: Full card number
        
    Returns:
        Masked card number (e.g., 6219-86**-****-1234)
    """
    if not card_number:
        return ''
    
    # Remove non-digits
    digits = ''.join(filter(str.isdigit, card_number))
    
    if len(digits) < 16:
        return card_number
    
    # Show first 6 and last 4 digits
    return f"{digits[:4]}-{digits[4:6]}**-****-{digits[-4:]}"
