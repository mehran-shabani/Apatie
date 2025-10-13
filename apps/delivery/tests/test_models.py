"""Model tests for delivery orders."""
import pytest


@pytest.mark.django_db
def test_mark_delivery_flow(delivery_factory):
    delivery = delivery_factory()
    delivery.mark_in_transit()
    delivery.refresh_from_db()
    assert delivery.status == delivery.Status.IN_TRANSIT
    delivery.mark_delivered()
    delivery.refresh_from_db()
    assert delivery.status == delivery.Status.DELIVERED
    assert delivery.delivered_at is not None
