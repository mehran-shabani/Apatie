"""
Vendor models for Apatye project.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class Vendor(TimeStampedModel):
    """
    Service provider/vendor model.
    """
    class VendorType(models.TextChoices):
        DOCTOR = 'doctor', _('Doctor')
        DELIVERY = 'delivery', _('Delivery Service')
        OTHER = 'other', _('Other')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('User')
    )
    
    name = models.CharField(_('Business name'), max_length=200)
    vendor_type = models.CharField(
        _('Vendor type'),
        max_length=20,
        choices=VendorType.choices,
        default=VendorType.DOCTOR
    )
    
    description = models.TextField(_('Description'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    
    is_verified = models.BooleanField(_('Verified'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Business info
    license_number = models.CharField(_('License number'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        db_table = 'vendors'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
