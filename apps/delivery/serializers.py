"""Serializers for delivery orders."""
from rest_framework import serializers

from .models import DeliveryOrder


class DeliveryOrderSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryOrder model."""

    class Meta:
        model = DeliveryOrder
        fields = (
            'id',
            'appointment',
            'address',
            'scheduled_for',
            'status',
            'delivered_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'delivered_at', 'created_at', 'updated_at')
