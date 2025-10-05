"""Appointment models."""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class AppointmentQuerySet(models.QuerySet):
    """Custom queryset helpers for appointments."""

    def active(self):
        """Return appointments that are not completed, cancelled, or expired."""

        return self.exclude(status__in=[
            self.model.Status.COMPLETED,
            self.model.Status.CANCELLED,
            self.model.Status.EXPIRED,
        ])

    def expired(self, reference_time=None):
        """Return active appointments whose end time has passed."""

        reference_time = reference_time or timezone.now()
        return self.active().filter(end_time__lt=reference_time)


class Appointment(TimeStampedModel):
    """Represents a scheduled appointment between a customer and a vendor."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        IN_PROGRESS = 'in_progress', _('In progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        EXPIRED = 'expired', _('Expired')

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Customer'),
    )
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Vendor'),
    )
    title = models.CharField(_('Title'), max_length=200)
    start_time = models.DateTimeField(_('Start time'))
    end_time = models.DateTimeField(_('End time'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField(_('Notes'), blank=True)
    status_updated_at = models.DateTimeField(_('Status updated at'), auto_now=True)

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        db_table = 'appointments'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status', 'end_time'], name='appointments_status_end'),
            models.Index(fields=['vendor', 'start_time'], name='appointments_vendor_start'),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_time:%Y-%m-%d %H:%M})"

    def mark_expired(self, reference_time=None):
        """Mark the appointment as expired if its end time has passed."""

        reference_time = reference_time or timezone.now()
        if self.status not in {self.Status.CANCELLED, self.Status.COMPLETED, self.Status.EXPIRED} and self.end_time < reference_time:
            self.status = self.Status.EXPIRED
            self.save(update_fields=['status', 'status_updated_at'])
        return self
