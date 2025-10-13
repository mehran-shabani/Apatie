"""Service layer tests for vendors."""
import pytest

from apps.vendors.services import deactivate_vendor, verify_vendor


@pytest.mark.django_db
def test_verify_vendor_marks_active(vendor_factory):
    vendor = vendor_factory(is_verified=False, is_active=False)
    verify_vendor(vendor)
    vendor.refresh_from_db()
    assert vendor.is_verified is True
    assert vendor.is_active is True


@pytest.mark.django_db
def test_deactivate_vendor_sets_flag(vendor_factory):
    vendor = vendor_factory()
    deactivate_vendor(vendor)
    vendor.refresh_from_db()
    assert vendor.is_active is False
