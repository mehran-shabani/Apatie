"""
Vendor admin configurations.
"""
from django.contrib import admin
from apps.common.admin import TimeStampedAdmin

from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(TimeStampedAdmin):
    """Admin for Vendor model."""
    list_display = ('name', 'user', 'vendor_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('vendor_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('name', 'user__mobile', 'phone', 'license_number')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'vendor_type')
        }),
        ('Contact Info', {
            'fields': ('phone', 'address')
        }),
        ('Business Info', {
            'fields': ('description', 'license_number', 'is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
