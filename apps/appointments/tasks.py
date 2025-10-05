"""
Celery tasks for appointments app.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_appointments():
    """
    Cleanup expired appointments.
    This task runs daily via Celery Beat.
    """
    logger.info('Running cleanup_expired_appointments task')
    # TODO: Implement cleanup logic
    return 'Cleanup completed'
