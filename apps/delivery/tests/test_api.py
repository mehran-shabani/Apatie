"""API tests for delivery orders."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_customer_can_view_related_delivery(api_client, delivery_factory):
    delivery = delivery_factory()
    api_client.force_authenticate(user=delivery.appointment.customer)
    url = reverse('delivery-order-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    assert payload['results'][0]['appointment'] == delivery.appointment_id


@pytest.mark.django_db
def test_vendor_can_view_delivery(api_client, delivery_factory):
    delivery = delivery_factory()
    api_client.force_authenticate(user=delivery.appointment.vendor.user)
    url = reverse('delivery-order-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    assert payload['results'][0]['appointment'] == delivery.appointment_id
