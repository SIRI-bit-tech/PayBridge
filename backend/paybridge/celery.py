import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')

app = Celery('paybridge')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks for billing
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'billing.check_expired_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'sync-usage-to-database': {
        'task': 'billing.sync_usage_to_database',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
