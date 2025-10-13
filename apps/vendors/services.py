"""Domain services for vendor lifecycle management."""
from django.db import transaction

from .models import Vendor


@transaction.atomic
def verify_vendor(vendor: Vendor) -> Vendor:
    """Mark the vendor as verified and active."""

    vendor.is_verified = True
    vendor.is_active = True
    vendor.save(update_fields=['is_verified', 'is_active'])
    return vendor


@transaction.atomic
def deactivate_vendor(vendor: Vendor) -> Vendor:
    """Deactivate the vendor without deleting the record."""

    vendor.is_active = False
    vendor.save(update_fields=['is_active'])
    return vendor
