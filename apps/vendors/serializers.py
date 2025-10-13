"""Serializers for the vendors app."""
from rest_framework import serializers

from .models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    """Serializer exposing vendor information."""

    user_mobile = serializers.CharField(source='user.mobile', read_only=True)

    class Meta:
        model = Vendor
        fields = (
            'id',
            'user',
            'user_mobile',
            'name',
            'vendor_type',
            'description',
            'phone',
            'address',
            'is_verified',
            'is_active',
            'license_number',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user_mobile',
            'created_at',
            'updated_at',
        )
