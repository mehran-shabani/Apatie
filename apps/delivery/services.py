"""Delivery domain services."""
from django.db import transaction

from .models import DeliveryOrder


@transaction.atomic
def schedule_delivery(*, appointment, address: str, scheduled_for=None) -> DeliveryOrder:
    """Create a delivery order for the appointment."""

    scheduled_for = scheduled_for or appointment.end_time
    return DeliveryOrder.objects.create(
        appointment=appointment,
        address=address,
        scheduled_for=scheduled_for,
    )


@transaction.atomic
def mark_delivery_in_transit(delivery: DeliveryOrder) -> DeliveryOrder:
    """Mark the delivery as in transit."""

    return delivery.mark_in_transit()


@transaction.atomic
def mark_delivery_completed(delivery: DeliveryOrder, *, timestamp=None) -> DeliveryOrder:
    """Mark the delivery as completed."""

    return delivery.mark_delivered(timestamp=timestamp)
