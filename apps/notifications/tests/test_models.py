"""Model tests for notifications."""
import pytest


@pytest.mark.django_db
def test_mark_read_updates_state(notification_factory):
    notification = notification_factory()
    notification.mark_read()
    notification.refresh_from_db()
    assert notification.is_read is True
    assert notification.read_at is not None
