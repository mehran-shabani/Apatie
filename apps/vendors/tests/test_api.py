"""API tests for vendors."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_vendor_list_returns_verified_entries(api_client, user_factory, vendor_factory):
    """Customers should see only verified vendors."""

    visible_vendor = vendor_factory(name='Visible Clinic', is_verified=True, is_active=True)
    vendor_factory(name='Hidden Clinic', is_verified=False, is_active=True)
    customer = user_factory()
    api_client.force_authenticate(user=customer)

    url = reverse('vendor-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    names = [item['name'] for item in payload['results']]
    assert names == ['Visible Clinic']


@pytest.mark.django_db
def test_staff_can_verify_vendor(api_client, vendor_factory, user_factory):
    """Staff users should be able to verify vendors via action."""

    vendor = vendor_factory(is_verified=False, is_active=False)
    staff = user_factory(user_type='admin')
    staff.is_staff = True
    staff.save()

    api_client.force_authenticate(user=staff)
    url = reverse('vendor-verify', args=[vendor.pk])
    response = api_client.post(url)
    assert response.status_code == 200
    vendor.refresh_from_db()
    assert vendor.is_verified is True
    assert vendor.is_active is True
