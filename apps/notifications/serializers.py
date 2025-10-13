"""Serializers for notifications."""
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer representing a notification."""

    class Meta:
        model = Notification
        fields = (
            'id',
            'recipient',
            'title',
            'message',
            'notification_type',
            'is_read',
            'read_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'is_read', 'read_at', 'created_at', 'updated_at')
