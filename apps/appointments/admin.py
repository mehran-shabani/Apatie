"""Admin configuration for appointments."""
from django.contrib import admin

from apps.common.admin import TimeStampedAdmin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(TimeStampedAdmin):
    """Admin interface for Appointment."""

    list_display = ('title', 'customer', 'vendor', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'vendor', 'start_time')
    search_fields = ('title', 'customer__mobile', 'vendor__name')
    ordering = ('-start_time',)
    readonly_fields = TimeStampedAdmin.readonly_fields + ('status_updated_at',)
