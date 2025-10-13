"""Global pytest fixtures for the Apatye project."""
from datetime import timedelta
from decimal import Decimal
import uuid

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.appointments.models import Appointment
from apps.delivery.models import DeliveryOrder
from apps.notifications.models import Notification
from apps.services.models import Service
from apps.vendors.models import Vendor


@pytest.fixture
def api_client():
    """Return a DRF APIClient instance."""

    return APIClient()


@pytest.fixture
def user_factory(django_user_model):
    """Factory for creating users."""

    def create_user(**kwargs):
        unique_mobile = kwargs.pop('mobile', None) or f"09{uuid.uuid4().hex[:9]}"
        defaults = {
            'password': 'test-password',
            'user_type': 'customer',
        }
        defaults.update(kwargs)
        user = django_user_model.objects.create_user(
            mobile=unique_mobile,
            password=defaults.pop('password'),
            **defaults,
        )
        return user

    return create_user


@pytest.fixture
def vendor_factory(user_factory):
    """Factory for creating vendors."""

    def create_vendor(**kwargs):
        user = kwargs.pop('user', None) or user_factory(user_type='vendor')
        defaults = {
            'name': 'Test Vendor',
            'vendor_type': Vendor.VendorType.DOCTOR,
            'description': 'Experienced provider',
            'phone': '02112345678',
            'address': 'Abadeh, IR',
            'is_verified': True,
            'is_active': True,
        }
        defaults.update(kwargs)
        vendor = Vendor.objects.create(user=user, **defaults)
        return vendor

    return create_vendor


@pytest.fixture
def service_factory(vendor_factory):
    """Factory for creating services."""

    def create_service(**kwargs):
        vendor = kwargs.pop('vendor', None) or vendor_factory()
        defaults = {
            'name': 'General Consultation',
            'description': '30 minute consultation',
            'base_price': Decimal('250000.00'),
            'is_active': True,
        }
        defaults.update(kwargs)
        return Service.objects.create(vendor=vendor, **defaults)

    return create_service


@pytest.fixture
def appointment_factory(user_factory, vendor_factory):
    """Factory for creating appointments."""

    def create_appointment(**kwargs):
        customer = kwargs.pop('customer', None) or user_factory()
        vendor = kwargs.pop('vendor', None) or vendor_factory()
        start_time = kwargs.pop('start_time', timezone.now() + timedelta(hours=1))
        end_time = kwargs.pop('end_time', start_time + timedelta(hours=1))
        defaults = {
            'title': 'Consultation',
            'notes': 'Bring previous reports.',
            'status': Appointment.Status.SCHEDULED,
        }
        defaults.update(kwargs)
        return Appointment.objects.create(
            customer=customer,
            vendor=vendor,
            start_time=start_time,
            end_time=end_time,
            **defaults,
        )

    return create_appointment


@pytest.fixture
def notification_factory(user_factory):
    """Factory for creating notifications."""

    def create_notification(**kwargs):
        recipient = kwargs.pop('recipient', None) or user_factory()
        defaults = {
            'title': 'Reminder',
            'message': 'Your appointment is tomorrow.',
            'notification_type': Notification.NotificationType.REMINDER,
        }
        defaults.update(kwargs)
        return Notification.objects.create(recipient=recipient, **defaults)

    return create_notification


@pytest.fixture
def delivery_factory(appointment_factory):
    """Factory for creating delivery orders."""

    def create_delivery(**kwargs):
        appointment = kwargs.pop('appointment', None) or appointment_factory()
        defaults = {
            'address': 'Abadeh, IR - Street 1',
            'scheduled_for': appointment.end_time,
        }
        defaults.update(kwargs)
        return DeliveryOrder.objects.create(appointment=appointment, **defaults)

    return create_delivery
