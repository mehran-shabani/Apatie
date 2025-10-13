"""Service layer for notifications."""
from django.db import transaction

from .models import Notification


@transaction.atomic
def send_notification(*, recipient, title: str, message: str, notification_type: str = Notification.NotificationType.GENERAL) -> Notification:
    """Create and return a notification record."""

    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
    )
