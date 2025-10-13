"""Service tests for appointments."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.appointments.services import schedule_appointment
from apps.notifications.models import Notification


@pytest.mark.django_db
def test_schedule_appointment_creates_notifications_and_delivery(user_factory, vendor_factory):
    customer = user_factory()
    vendor = vendor_factory()
    start = timezone.now() + timedelta(hours=2)
    end = start + timedelta(hours=1)

    appointment = schedule_appointment(
        customer=customer,
        vendor=vendor,
        title='Follow up',
        start_time=start,
        end_time=end,
        notes='Discuss lab results.',
        delivery_address='Abadeh, Main street',
    )

    assert appointment.customer == customer
    assert appointment.vendor == vendor
    assert Notification.objects.filter(recipient=customer).exists()
    assert Notification.objects.filter(recipient=vendor.user).exists()
    assert hasattr(appointment, 'delivery_order')
    assert appointment.delivery_order.address == 'Abadeh, Main street'
