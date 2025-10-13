"""API tests for appointments."""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_customer_can_schedule_appointment(api_client, user_factory, vendor_factory):
    customer = user_factory()
    vendor = vendor_factory()
    api_client.force_authenticate(user=customer)

    url = reverse('appointment-list')
    payload = {
        'vendor': vendor.id,
        'title': 'Dental checkup',
        'start_time': (timezone.now() + timedelta(hours=3)).isoformat(),
        'end_time': (timezone.now() + timedelta(hours=4)).isoformat(),
        'notes': 'Please bring dental x-rays.',
        'delivery_address': 'Abadeh, Clinic road',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201
    assert response.data['vendor'] == vendor.id
    assert response.data['title'] == 'Dental checkup'


@pytest.mark.django_db
def test_vendor_sees_their_appointments(api_client, appointment_factory, vendor_factory):
    vendor = vendor_factory()
    other_vendor = vendor_factory(name='Other Vendor')
    appointment_factory(vendor=vendor)
    appointment_factory(vendor=other_vendor)

    api_client.force_authenticate(user=vendor.user)
    url = reverse('appointment-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    assert payload['results'][0]['vendor'] == vendor.id
