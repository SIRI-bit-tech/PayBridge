import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')

app = Celery('paybridge')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks for billing and webhooks
app.conf.beat_schedule = {
    # Billing tasks commented out - implement these in billing_tasks.py if needed
    # 'check-expired-subscriptions': {
    #     'task': 'billing.check_expired_subscriptions',
    #     'schedule': crontab(hour=0, minute=0),
    # },
    # 'sync-usage-to-database': {
    #     'task': 'billing.sync_usage_to_database',
    #     'schedule': crontab(minute='*/30'),
    # },
    'retry-failed-webhook-deliveries': {
        'task': 'api.webhook_tasks.retry_failed_deliveries',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'calculate-webhook-metrics': {
        'task': 'api.webhook_tasks.calculate_webhook_metrics',
        'schedule': crontab(minute=0),  # Every hour
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
