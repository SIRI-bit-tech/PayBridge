"""
Celery tasks for webhook processing and delivery
Handles async processing, retries, and delivery guarantees
"""
import logging
import requests
import json
import time
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction as db_transaction
from datetime import timedelta
from .webhook_models import (
    WebhookEvent, WebhookSubscription, WebhookDeliveryLog, WebhookDeliveryMetrics
)
from .models import Transaction, AuditLog
from .billing_models import Payment, BillingSubscription
from .redis_pubsub import publish_event

logger = logging.getLogger(__name__)

# Retry schedule: 1min, 10min, 1hr, 6hr, 24hr
RETRY_SCHEDULE = [60, 600, 3600, 21600, 86400]
MAX_RETRIES = len(RETRY_SCHEDULE)


@shared_task(bind=True, max_retries=3)
def process_provider_webhook(self, webhook_event_id):
    """
    Process incoming provider webhook event
    Updates internal state and triggers client webhook deliveries
    """
    try:
        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        
        # Check if already processed (idempotency)
        if webhook_event.processing_status == 'succeeded':
            logger.info(f"Webhook event {webhook_event_id} already processed")
            return
        
        # Mark as processing
        webhook_event.processing_status = 'processing'
        webhook_event.save(update_fields=['processing_status', 'updated_at'])
        
        # Process based on canonical event type
        canonical_type = webhook_event.canonical_event_type
        raw_data = webhook_event.raw_payload
        
        if canonical_type.startswith('payment.'):
            _process_payment_event(webhook_event, canonical_type, raw_data)
        elif canonical_type.startswith('subscription.'):
            _process_subscription_event(webhook_event, canonical_type, raw_data)
        elif canonical_type.startswith('kyc.'):
            _process_kyc_event(webhook_event, canonical_type, raw_data)
        elif canonical_type.startswith('transfer.'):
            _process_transfer_event(webhook_event, canonical_type, raw_data)
        else:
            logger.warning(f"Unknown event type: {canonical_type}")
        
        # Mark as succeeded
        webhook_event.processing_status = 'succeeded'
        webhook_event.processed_at = timezone.now()
        webhook_event.save(update_fields=['processing_status', 'processed_at', 'updated_at'])
        
        # Publish to Redis for real-time updates
        publish_event('bridge_events', {
            'type': canonical_type,
            'event_id': str(webhook_event.id),
            'provider': webhook_event.provider,
            'timestamp': timezone.now().isoformat()
        })
        
        # Trigger client webhook deliveries
        trigger_client_webhooks.delay(str(webhook_event.id), canonical_type)
        
        logger.info(f"Successfully processed webhook event: {webhook_event_id}")
        
    except WebhookEvent.DoesNotExist:
        logger.error(f"Webhook event {webhook_event_id} not found")
    except Exception as e:
        logger.error(f"Error processing webhook event {webhook_event_id}: {str(e)}", exc_info=True)
        
        # Mark as failed
        try:
            webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
            webhook_event.processing_status = 'failed'
            webhook_event.processing_error = str(e)
            webhook_event.save(update_fields=['processing_status', 'processing_error', 'updated_at'])
        except:
            pass
        
        # Retry with exponential backoff
        if self.request.retries < 3:
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)


def _process_payment_event(webhook_event, event_type, data):
    """Process payment-related events"""
    provider = webhook_event.provider
    event_data = data.get('data', {})
    
    # Extract transaction reference based on provider
    if provider == 'paystack':
        reference = event_data.get('reference')
    elif provider == 'flutterwave':
        reference = event_data.get('tx_ref')
    elif provider == 'stripe':
        reference = event_data.get('object', {}).get('id')
    else:
        reference = None
    
    if not reference:
        logger.warning(f"No reference found in payment event: {webhook_event.id}")
        return
    
    # Find transaction
    transaction = Transaction.objects.filter(reference=reference).first()
    
    if transaction:
        # Update transaction status
        if event_type == 'payment.completed':
            transaction.status = 'completed'
            transaction.provider_response = data
            transaction.save(update_fields=['status', 'provider_response', 'updated_at'])
            logger.info(f"Transaction {transaction.id} marked as completed")
        elif event_type == 'payment.failed':
            transaction.status = 'failed'
            transaction.provider_response = data
            transaction.save(update_fields=['status', 'provider_response', 'updated_at'])
            logger.info(f"Transaction {transaction.id} marked as failed")
    
    # Check if it's a billing payment
    payment = Payment.objects.filter(transaction_id=reference).first()
    
    if payment:
        if event_type == 'payment.completed':
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.provider_response = data
            payment.save(update_fields=['status', 'completed_at', 'provider_response', 'updated_at'])
            
            # Upgrade subscription
            if payment.subscription:
                payment.subscription.status = 'active'
                payment.subscription.save(update_fields=['status', 'updated_at'])
                logger.info(f"Subscription {payment.subscription.id} activated")
        elif event_type == 'payment.failed':
            payment.status = 'failed'
            payment.error_message = event_data.get('message', 'Payment failed')
            payment.provider_response = data
            payment.save(update_fields=['status', 'error_message', 'provider_response', 'updated_at'])


def _process_subscription_event(webhook_event, event_type, data):
    """Process subscription-related events"""
    logger.info(f"Processing subscription event: {event_type}")
    # Add subscription processing logic here


def _process_kyc_event(webhook_event, event_type, data):
    """Process KYC-related events"""
    logger.info(f"Processing KYC event: {event_type}")
    # Add KYC processing logic here


def _process_transfer_event(webhook_event, event_type, data):
    """Process transfer/payout events"""
    logger.info(f"Processing transfer event: {event_type}")
    # Add transfer processing logic here


@shared_task
def trigger_client_webhooks(webhook_event_id, event_type):
    """
    Trigger delivery to all client webhook subscriptions
    that are subscribed to this event type
    """
    try:
        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        
        # Find all active subscriptions for this event type
        subscriptions = WebhookSubscription.objects.filter(
            active=True,
            selected_events__contains=[event_type]
        )
        
        logger.info(f"Triggering {subscriptions.count()} client webhooks for event {event_type}")
        
        for subscription in subscriptions:
            # Queue delivery for each subscription
            deliver_client_webhook.delay(
                str(subscription.id),
                str(webhook_event.id),
                event_type,
                attempt_number=1
            )
    
    except WebhookEvent.DoesNotExist:
        logger.error(f"Webhook event {webhook_event_id} not found")
    except Exception as e:
        logger.error(f"Error triggering client webhooks: {str(e)}", exc_info=True)


@shared_task(bind=True)
def deliver_client_webhook(self, subscription_id, webhook_event_id, event_type, attempt_number=1):
    """
    Deliver webhook to a single client endpoint
    Implements exponential backoff retry logic
    """
    try:
        subscription = WebhookSubscription.objects.get(id=subscription_id)
        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        
        # Check for duplicate delivery (idempotency)
        existing_success = WebhookDeliveryLog.objects.filter(
            webhook_subscription=subscription,
            event_id=webhook_event.id,
            status='success'
        ).exists()
        
        if existing_success:
            logger.info(f"Webhook already delivered successfully: {subscription_id} - {webhook_event_id}")
            return
        
        # Prepare payload
        timestamp = int(time.time())
        payload = {
            'id': str(webhook_event.id),
            'type': event_type,
            'created': timestamp,
            'data': webhook_event.raw_payload.get('data', {}),
            'provider': webhook_event.provider
        }
        
        # Generate signature
        signature = subscription.generate_signature(payload, timestamp)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-PayBridge-Signature': signature,
            'X-PayBridge-Timestamp': str(timestamp),
            'X-PayBridge-Event-Type': event_type,
            'X-PayBridge-Event-ID': str(webhook_event.id),
            'User-Agent': 'PayBridge-Webhooks/1.0'
        }
        
        # Create delivery log
        delivery_log = WebhookDeliveryLog.objects.create(
            webhook_subscription=subscription,
            webhook_event=webhook_event,
            event_id=webhook_event.id,
            event_type=event_type,
            attempt_number=attempt_number,
            status='pending'
        )
        
        # Send webhook
        start_time = time.time()
        
        try:
            response = requests.post(
                subscription.url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Check response
            if 200 <= response.status_code < 300:
                # Success
                delivery_log.status = 'success'
                delivery_log.http_status_code = response.status_code
                delivery_log.response_body = response.text[:1000]  # Truncate
                delivery_log.latency_ms = latency_ms
                delivery_log.save()
                
                # Update subscription stats
                subscription.last_delivery_status = 'healthy'
                subscription.last_delivery_at = timezone.now()
                subscription.success_count += 1
                subscription.failure_count = 0  # Reset failure count
                subscription.save()
                
                logger.info(f"Webhook delivered successfully: {subscription.url} - {event_type}")
                
            elif response.status_code == 410:
                # Endpoint gone - disable subscription
                delivery_log.status = 'failed'
                delivery_log.http_status_code = response.status_code
                delivery_log.error_message = "Endpoint returned 410 Gone"
                delivery_log.save()
                
                subscription.active = False
                subscription.last_delivery_status = 'disabled'
                subscription.save()
                
                logger.warning(f"Webhook endpoint disabled (410 Gone): {subscription.url}")
                
            else:
                # Failed - schedule retry
                delivery_log.status = 'failed'
                delivery_log.http_status_code = response.status_code
                delivery_log.response_body = response.text[:1000]
                delivery_log.error_message = f"HTTP {response.status_code}"
                
                # Schedule retry if not max attempts
                if attempt_number < MAX_RETRIES:
                    retry_delay = RETRY_SCHEDULE[attempt_number - 1]
                    next_retry = timezone.now() + timedelta(seconds=retry_delay)
                    delivery_log.next_retry_at = next_retry
                    delivery_log.save()
                    
                    # Schedule retry task
                    deliver_client_webhook.apply_async(
                        args=[subscription_id, webhook_event_id, event_type, attempt_number + 1],
                        countdown=retry_delay
                    )
                    
                    logger.info(f"Webhook delivery failed, retry scheduled: {subscription.url} - Attempt {attempt_number}")
                else:
                    # Max retries reached - dead letter
                    delivery_log.status = 'dead_letter'
                    delivery_log.save()
                    
                    subscription.last_delivery_status = 'failing'
                    subscription.failure_count += 1
                    subscription.save()
                    
                    logger.error(f"Webhook delivery failed permanently: {subscription.url} - {event_type}")
                
        except requests.exceptions.Timeout:
            latency_ms = int((time.time() - start_time) * 1000)
            delivery_log.status = 'failed'
            delivery_log.error_message = "Request timeout"
            delivery_log.latency_ms = latency_ms
            
            # Schedule retry
            if attempt_number < MAX_RETRIES:
                retry_delay = RETRY_SCHEDULE[attempt_number - 1]
                next_retry = timezone.now() + timedelta(seconds=retry_delay)
                delivery_log.next_retry_at = next_retry
                delivery_log.save()
                
                deliver_client_webhook.apply_async(
                    args=[subscription_id, webhook_event_id, event_type, attempt_number + 1],
                    countdown=retry_delay
                )
            else:
                delivery_log.status = 'dead_letter'
                delivery_log.save()
                
        except requests.exceptions.RequestException as e:
            delivery_log.status = 'failed'
            delivery_log.error_message = str(e)
            delivery_log.save()
            
            # Schedule retry
            if attempt_number < MAX_RETRIES:
                retry_delay = RETRY_SCHEDULE[attempt_number - 1]
                next_retry = timezone.now() + timedelta(seconds=retry_delay)
                delivery_log.next_retry_at = next_retry
                delivery_log.save()
                
                deliver_client_webhook.apply_async(
                    args=[subscription_id, webhook_event_id, event_type, attempt_number + 1],
                    countdown=retry_delay
                )
            else:
                delivery_log.status = 'dead_letter'
                delivery_log.save()
        
        # Publish delivery status to Redis
        publish_event('webhook_deliveries', {
            'subscription_id': str(subscription.id),
            'event_id': str(webhook_event.id),
            'status': delivery_log.status,
            'attempt': attempt_number,
            'timestamp': timezone.now().isoformat()
        })
        
    except (WebhookSubscription.DoesNotExist, WebhookEvent.DoesNotExist) as e:
        logger.error(f"Webhook delivery failed - not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error delivering webhook: {str(e)}", exc_info=True)


@shared_task
def retry_failed_deliveries():
    """
    Periodic task to retry failed webhook deliveries
    Runs every 5 minutes to check for scheduled retries
    """
    try:
        now = timezone.now()
        
        # Find deliveries scheduled for retry
        pending_retries = WebhookDeliveryLog.objects.filter(
            status='failed',
            next_retry_at__lte=now,
            attempt_number__lt=MAX_RETRIES
        )
        
        logger.info(f"Found {pending_retries.count()} webhook deliveries to retry")
        
        for delivery in pending_retries:
            deliver_client_webhook.delay(
                str(delivery.webhook_subscription.id),
                str(delivery.webhook_event.id),
                delivery.event_type,
                delivery.attempt_number + 1
            )
    
    except Exception as e:
        logger.error(f"Error retrying failed deliveries: {str(e)}", exc_info=True)


@shared_task
def calculate_webhook_metrics():
    """
    Calculate webhook delivery metrics for monitoring
    Runs hourly to aggregate stats
    """
    try:
        from django.db.models import Count, Avg
        import numpy as np
        
        now = timezone.now()
        period_start = now - timedelta(hours=1)
        
        subscriptions = WebhookSubscription.objects.filter(active=True)
        
        for subscription in subscriptions:
            deliveries = WebhookDeliveryLog.objects.filter(
                webhook_subscription=subscription,
                created_at__gte=period_start,
                created_at__lt=now
            )
            
            if not deliveries.exists():
                continue
            
            total = deliveries.count()
            successful = deliveries.filter(status='success').count()
            failed = deliveries.filter(status='failed').count()
            dead_letter = deliveries.filter(status='dead_letter').count()
            retries = deliveries.filter(attempt_number__gt=1).count()
            
            # Calculate latency percentiles
            latencies = list(deliveries.filter(
                latency_ms__isnull=False
            ).values_list('latency_ms', flat=True))
            
            if latencies:
                avg_latency = np.mean(latencies)
                p95_latency = np.percentile(latencies, 95)
                p99_latency = np.percentile(latencies, 99)
            else:
                avg_latency = p95_latency = p99_latency = 0
            
            # Create or update metrics
            WebhookDeliveryMetrics.objects.update_or_create(
                webhook_subscription=subscription,
                period_start=period_start,
                defaults={
                    'period_end': now,
                    'total_deliveries': total,
                    'successful_deliveries': successful,
                    'failed_deliveries': failed,
                    'retry_count': retries,
                    'dead_letter_count': dead_letter,
                    'avg_latency_ms': avg_latency,
                    'p95_latency_ms': p95_latency,
                    'p99_latency_ms': p99_latency
                }
            )
        
        logger.info(f"Calculated webhook metrics for {subscriptions.count()} subscriptions")
        
    except Exception as e:
        logger.error(f"Error calculating webhook metrics: {str(e)}", exc_info=True)
