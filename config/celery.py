"""
Celery configuration for Apatye project.
"""
import os

from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('apatye')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')


# Celery Beat schedule
app.conf.beat_schedule = {
    'cleanup-expired-appointments': {
        'task': 'apps.appointments.tasks.cleanup_expired_appointments',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
    'reconcile-pending-payments': {
        'task': 'apps.billing.tasks.reconcile_pending_payments',
        'schedule': crontab(hour='*/4', minute=0),  # Every 4 hours
    },
    'check-expired-subscriptions': {
        'task': 'apps.billing.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=3, minute=0),  # Every day at 3:00 AM
    },
    'send-subscription-expiry-reminders': {
        'task': 'apps.billing.tasks.send_subscription_expiry_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
    },
}
