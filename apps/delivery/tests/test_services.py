"""Service tests for delivery domain."""
import pytest

from apps.delivery.services import mark_delivery_completed, mark_delivery_in_transit, schedule_delivery


@pytest.mark.django_db
def test_schedule_delivery_creates_order(appointment_factory):
    appointment = appointment_factory()
    delivery = schedule_delivery(appointment=appointment, address='Street 1, Abadeh')
    assert delivery.appointment == appointment
    assert delivery.address == 'Street 1, Abadeh'


@pytest.mark.django_db
def test_mark_delivery_transitions(delivery_factory):
    delivery = delivery_factory()
    mark_delivery_in_transit(delivery)
    delivery.refresh_from_db()
    assert delivery.status == delivery.Status.IN_TRANSIT
    mark_delivery_completed(delivery)
    delivery.refresh_from_db()
    assert delivery.status == delivery.Status.DELIVERED
