"""Service layer for appointment scheduling."""
from typing import Optional

from django.db import transaction

from apps.delivery.services import schedule_delivery
from apps.notifications.services import send_notification

from .models import Appointment


@transaction.atomic
def schedule_appointment(*, customer, vendor, title: str, start_time, end_time, notes: str = '', delivery_address: Optional[str] = None) -> Appointment:
    """Create an appointment and trigger the associated side effects."""

    appointment = Appointment.objects.create(
        customer=customer,
        vendor=vendor,
        title=title,
        start_time=start_time,
        end_time=end_time,
        notes=notes,
    )

    send_notification(
        recipient=customer,
        title='Appointment scheduled',
        message=f'Your appointment "{title}" with {vendor.name} is scheduled.',
        notification_type='appointment',
    )
    send_notification(
        recipient=vendor.user,
        title='New appointment booked',
        message=f'{customer.mobile} booked "{title}".',
        notification_type='appointment',
    )

    if delivery_address:
        schedule_delivery(
            appointment=appointment,
            address=delivery_address,
            scheduled_for=end_time,
        )

    appointment.refresh_from_db()
    return appointment
