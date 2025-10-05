"""Celery tasks for appointments app."""
import logging
from datetime import datetime
from typing import Optional

from celery import shared_task
from django.apps import apps
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def mark_expired_appointments(reference_time: Optional[datetime] = None) -> int:
    """Mark appointments whose end time has passed as expired."""

    Appointment = apps.get_model('appointments', 'Appointment')
    reference_time = reference_time or timezone.now()
    expired_qs = Appointment.objects.active().expired(reference_time)

    if not expired_qs.exists():
        return 0

    with transaction.atomic():
        updated = expired_qs.update(
            status=Appointment.Status.EXPIRED,
            status_updated_at=reference_time,
        )
    return updated


@shared_task(bind=True, ignore_result=False)
def cleanup_expired_appointments(self):
    """Cleanup expired appointments.

    This task runs daily via Celery Beat to ensure old appointments are marked
    as expired. It logs the outcome so operators can monitor the cleanup.
    """

    try:
        updated = mark_expired_appointments()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception('Failed to cleanup expired appointments: %s', exc)
        raise

    if updated:
        logger.info('Marked %s appointment(s) as expired.', updated)
    else:
        logger.info('No expired appointments found during cleanup.')
    return updated
