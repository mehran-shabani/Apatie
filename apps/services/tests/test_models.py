"""Model tests for services."""
import pytest


@pytest.mark.django_db
def test_service_queryset_active_filters_inactive(service_factory, vendor_factory):
    active_service = service_factory(is_active=True)
    service_factory(is_active=False)
    queryset = type(active_service).objects.active()
    assert list(queryset) == [active_service]
