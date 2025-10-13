"""Service models for Apatye project."""
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class ServiceQuerySet(models.QuerySet):
    """Custom queryset helpers for the service catalogue."""

    def active(self):
        """Return only services that are active and visible to customers."""

        return self.filter(is_active=True, vendor__is_active=True)


class Service(TimeStampedModel):
    """Represents a service that can be offered by a vendor."""

    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Vendor'),
    )
    name = models.CharField(_('Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    base_price = models.DecimalField(
        _('Base price'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    is_active = models.BooleanField(_('Is active'), default=True)

    objects = ServiceQuerySet.as_manager()

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        db_table = 'services'
        ordering = ['name']
        indexes = [
            models.Index(fields=['vendor', 'is_active'], name='services_vendor_active'),
        ]
        unique_together = ('vendor', 'name')

    def __str__(self):
        return f"{self.name} ({self.vendor.name})"

    def deactivate(self):
        """Deactivate the service so it is hidden from customers."""

        if self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])
        return self

    def activate(self):
        """Reactivate a previously deactivated service."""

        if not self.is_active:
            self.is_active = True
            self.save(update_fields=['is_active'])
        return self
