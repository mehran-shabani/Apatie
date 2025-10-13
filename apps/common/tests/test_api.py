"""API tests for the common app."""
import pytest


@pytest.mark.django_db
def test_health_check_endpoint(api_client):
    """Health check should return application metadata."""

    response = api_client.get('/health/')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] in {'healthy', 'degraded'}
    assert 'database' in payload
    assert 'redis' in payload
