from celery import shared_task
import requests
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from api.models import WebhookEvent, Webhook

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def send_webhook_async(self, webhook_event_id):
    """Celery task for asynchronous webhook delivery with exponential backoff"""
    try:
        event = WebhookEvent.objects.get(id=webhook_event_id)
        webhook = event.webhook
        
        # Generate HMAC signature
        payload = json.dumps(event.payload)
        signature = hmac.new(
            webhook.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-PayBridge-Signature': signature,
            'X-PayBridge-Event': event.event_type,
            'X-PayBridge-Delivery': str(event.attempt)
        }
        
        # Send webhook
        response = requests.post(
            webhook.url,
            data=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201, 204]:
            event.status = 'success'
            event.response_status_code = response.status_code
            event.save()
            webhook.last_triggered = datetime.now()
            webhook.save()
            logger.info(f"Webhook sent successfully: {webhook.url}")
        else:
            raise Exception(f"Webhook failed with status {response.status_code}")
    
    except Exception as exc:
        logger.error(f"Webhook delivery error: {str(exc)}")
        
        # Retry with exponential backoff: 5s, 30s, 5m, 30m, 3h
        retry_delays = [5, 30, 300, 1800, 10800]
        
        if self.request.retries < len(retry_delays):
            delay = retry_delays[self.request.retries]
            event.attempt = self.request.retries + 1
            event.save()
            
            raise self.retry(exc=exc, countdown=delay)
        else:
            # Final attempt failed
            event.status = 'failed'
            event.error_message = str(exc)
            event.save()
            logger.error(f"Webhook permanently failed: {webhook.url}")


class WebhookService:
    """Manage webhook subscriptions and delivery"""
    
    @staticmethod
    def trigger_event(user, event_type, payload):
        """Trigger webhook events for user"""
        webhooks = Webhook.objects.filter(
            user=user,
            is_active=True,
            event_types__contains=[event_type]
        )
        
        for webhook in webhooks:
            event = WebhookEvent.objects.create(
                webhook=webhook,
                event_type=event_type,
                payload=payload
            )
            
            # Queue async delivery
            send_webhook_async.delay(str(event.id))
    
    @staticmethod
    def create_webhook(user, url, event_types):
        """Create new webhook subscription"""
        webhook = Webhook.objects.create(
            user=user,
            url=url,
            event_types=event_types
        )
        return webhook
    
    @staticmethod
    def verify_webhook_signature(payload, signature, secret):
        """Verify incoming webhook signature"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
