"""Serializers for the services app."""
from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for the Service model."""

    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = Service
        fields = (
            'id',
            'vendor',
            'vendor_name',
            'name',
            'description',
            'base_price',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'vendor', 'created_at', 'updated_at', 'vendor_name')
