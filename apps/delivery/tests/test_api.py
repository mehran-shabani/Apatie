"""API tests for delivery orders."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('role', ['customer', 'vendor'])
def test_user_can_view_related_delivery(api_client, delivery_factory, role):
    delivery = delivery_factory()
    user = (
        delivery.appointment.customer
        if role == 'customer'
        else delivery.appointment.vendor.user
    )

    api_client.force_authenticate(user=user)
    url = reverse('delivery-order-list')
    response = api_client.get(url)

    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    assert payload['results'][0]['appointment'] == delivery.appointment_id
