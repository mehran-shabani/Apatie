"""Integration tests covering appointment flows across apps."""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.reverse import reverse

from apps.appointments.models import Appointment
from apps.notifications.models import Notification


@pytest.mark.django_db
@pytest.mark.integration
def test_booking_appointment_triggers_notification_and_delivery(api_client, user_factory, vendor_factory):
    customer = user_factory()
    vendor = vendor_factory()
    api_client.force_authenticate(user=customer)

    url = reverse('appointment-list')
    payload = {
        'vendor': vendor.id,
        'title': 'Therapy Session',
        'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
        'end_time': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        'delivery_address': 'Abadeh, Therapy Center',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201

    assert Notification.objects.filter(recipient=customer, title__icontains='scheduled').exists()
    assert Notification.objects.filter(recipient=vendor.user, title__icontains='New appointment').exists()

    appointment_id = response.data['id']
    appointment = Appointment.objects.get(pk=appointment_id)
    assert hasattr(appointment, 'delivery_order')
    assert appointment.delivery_order.address == 'Abadeh, Therapy Center'
