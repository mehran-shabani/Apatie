"""Service layer tests for the services domain."""
from decimal import Decimal

import pytest

from apps.services.services import toggle_service_availability, update_service_pricing


@pytest.mark.django_db
def test_toggle_service_availability(service_factory):
    service = service_factory(is_active=True)
    toggle_service_availability(service, is_active=False)
    service.refresh_from_db()
    assert service.is_active is False


@pytest.mark.django_db
def test_update_service_pricing(service_factory):
    service = service_factory(base_price=Decimal('100000.00'))
    update_service_pricing(service, base_price=Decimal('150000.00'))
    service.refresh_from_db()
    assert service.base_price == Decimal('150000.00')
