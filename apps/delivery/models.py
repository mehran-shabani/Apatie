"""Delivery models for the Apatye project."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class DeliveryOrder(TimeStampedModel):
    """Represents a delivery request associated with an appointment."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        IN_TRANSIT = 'in_transit', _('In transit')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='delivery_order',
        verbose_name=_('Appointment'),
    )
    address = models.TextField(_('Address'))
    scheduled_for = models.DateTimeField(_('Scheduled for'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    delivered_at = models.DateTimeField(_('Delivered at'), null=True, blank=True)

    class Meta:
        verbose_name = _('Delivery order')
        verbose_name_plural = _('Delivery orders')
        db_table = 'delivery_orders'
        ordering = ['-scheduled_for']

    def __str__(self):
        return f"Delivery for {self.appointment}"

    def mark_in_transit(self):
        """Mark the delivery as in transit."""

        self.status = self.Status.IN_TRANSIT
        self.save(update_fields=['status'])
        return self

    def mark_delivered(self, *, timestamp=None):
        """Mark the delivery as delivered."""

        self.status = self.Status.DELIVERED
        self.delivered_at = timestamp or timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
        return self
