"""Notification models for Apatye project."""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class NotificationQuerySet(models.QuerySet):
    """Helpful filters for notification workflows."""

    def unread(self):
        return self.filter(is_read=False)


class Notification(TimeStampedModel):
    """Represents a notification sent to a user."""

    class NotificationType(models.TextChoices):
        GENERAL = 'general', _('General')
        APPOINTMENT = 'appointment', _('Appointment')
        REMINDER = 'reminder', _('Reminder')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient'),
    )
    title = models.CharField(_('Title'), max_length=200)
    message = models.TextField(_('Message'))
    notification_type = models.CharField(
        _('Type'),
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    is_read = models.BooleanField(_('Is read'), default=False)
    read_at = models.DateTimeField(_('Read at'), null=True, blank=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read'], name='notification_recipient_read'),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient.mobile}"

    def mark_read(self, *, timestamp=None):
        """Mark the notification as read and record the timestamp."""

        if not self.is_read:
            self.is_read = True
            self.read_at = timestamp or timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
        return self
