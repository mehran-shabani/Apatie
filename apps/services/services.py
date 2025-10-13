"""Domain services for service management."""
from django.db import transaction

from .models import Service


@transaction.atomic
def toggle_service_availability(service: Service, *, is_active: bool) -> Service:
    """Toggle the availability of a service in an atomic transaction."""

    if is_active:
        service.activate()
    else:
        service.deactivate()
    return service


@transaction.atomic
def update_service_pricing(service: Service, *, base_price) -> Service:
    """Update the service price while ensuring data integrity."""

    service.base_price = base_price
    service.save(update_fields=['base_price'])
    return service
