"""API tests for user endpoints."""
import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_user_me_requires_authentication(api_client):
    """Unauthenticated requests should be rejected."""

    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


@pytest.mark.django_db
def test_user_me_returns_profile(api_client, user_factory):
    """Authenticated user should receive their profile data."""

    user = user_factory(first_name='Sara', last_name='Jafari')
    api_client.force_authenticate(user=user)
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['mobile'] == user.mobile
    assert response.data['first_name'] == 'Sara'
    assert response.data['last_name'] == 'Jafari'
