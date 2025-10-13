"""Serializers for appointments."""
from rest_framework import serializers

from .models import Appointment
from .services import schedule_appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model with delivery support."""

    customer_mobile = serializers.CharField(source='customer.mobile', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    delivery_address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = (
            'id',
            'customer',
            'customer_mobile',
            'vendor',
            'vendor_name',
            'title',
            'start_time',
            'end_time',
            'status',
            'notes',
            'delivery_address',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'customer',
            'status',
            'created_at',
            'updated_at',
            'customer_mobile',
            'vendor_name',
        )

    def create(self, validated_data):
        delivery_address = validated_data.pop('delivery_address', '').strip()
        appointment = schedule_appointment(
            customer=validated_data['customer'],
            vendor=validated_data['vendor'],
            title=validated_data['title'],
            start_time=validated_data['start_time'],
            end_time=validated_data['end_time'],
            notes=validated_data.get('notes', ''),
            delivery_address=delivery_address or None,
        )
        if validated_data.get('notes'):
            appointment.notes = validated_data['notes']
        return appointment

    def validate(self, attrs):
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError('End time must be after start time.')
        return super().validate(attrs)
