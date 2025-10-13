"""Model tests for vendors."""
import pytest


@pytest.mark.django_db
def test_vendor_string_representation(vendor_factory):
    """Vendor string should return business name."""

    vendor = vendor_factory(name='Clinic One')
    assert str(vendor) == 'Clinic One'
    assert vendor.user.vendor_profile == vendor
