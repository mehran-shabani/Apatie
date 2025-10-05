"""
Common admin configurations.
"""
from django.contrib import admin


class TimeStampedAdmin(admin.ModelAdmin):
    """
    Base admin class for timestamped models.
    """
    readonly_fields = ('created_at', 'updated_at')
