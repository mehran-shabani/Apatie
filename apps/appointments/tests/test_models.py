"""Model tests for appointments."""
from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_mark_expired_changes_status(appointment_factory):
    appointment = appointment_factory(
        end_time=timezone.now() - timedelta(minutes=1),
        status='scheduled',
    )
    appointment.mark_expired(reference_time=timezone.now())
    appointment.refresh_from_db()
    assert appointment.status == appointment.Status.EXPIRED
