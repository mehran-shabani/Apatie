"""API tests for notifications."""
import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_user_can_list_notifications(api_client, notification_factory):
    notification = notification_factory()
    api_client.force_authenticate(user=notification.recipient)
    url = reverse('notification-list')
    response = api_client.get(url)
    assert response.status_code == 200
    payload = response.data
    assert payload['count'] == 1
    assert payload['results'][0]['id'] == notification.id


@pytest.mark.django_db
def test_user_can_mark_notification_read(api_client, notification_factory):
    notification = notification_factory()
    api_client.force_authenticate(user=notification.recipient)
    url = reverse('notification-mark-read', args=[notification.pk])
    response = api_client.post(url)
    assert response.status_code == 200
    notification.refresh_from_db()
    assert notification.is_read is True
