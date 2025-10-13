"""Service tests for notifications."""
import pytest

from apps.notifications.services import send_notification


@pytest.mark.django_db
def test_send_notification_creates_record(user_factory):
    recipient = user_factory()
    notification = send_notification(
        recipient=recipient,
        title='System Alert',
        message='Appointment updated.',
        notification_type='general',
    )
    assert notification.recipient == recipient
    assert notification.title == 'System Alert'
