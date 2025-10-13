"""API tests for services."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_vendor_can_create_service(api_client, vendor_factory):
    vendor = vendor_factory()
    api_client.force_authenticate(user=vendor.user)

    url = reverse('service-list')
    payload = {
        'name': 'Home Visit',
        'description': 'Doctor home visit service',
        'base_price': '350000.00',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201
    assert response.data['name'] == 'Home Visit'
    assert response.data['vendor'] == vendor.id


@pytest.mark.django_db
def test_customer_sees_only_active_services(api_client, user_factory, service_factory):
    customer = user_factory()
    active_service = service_factory(is_active=True)
    service_factory(is_active=False)

    api_client.force_authenticate(user=customer)
    url = reverse('service-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    names = [item['name'] for item in payload['results']]
    assert names == [active_service.name]
