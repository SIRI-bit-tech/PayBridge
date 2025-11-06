from celery import shared_task
import logging
import requests
import hmac
import hashlib
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from .models import Webhook, Transaction, WebhookEvent, APILog, Invoice, UsageMetric
from .exceptions import WebhookDeliveryFailed
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 300  # 5 minutes


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_webhook(self, webhook_id, event_type, payload):
    """Send webhook asynchronously with exponential backoff retry logic"""
    try:
        webhook = Webhook.objects.get(id=webhook_id)
        
        # Check if webhook is active
        if not webhook.is_active:
            logger.warning(f"Webhook {webhook_id} is inactive")
            return
        
        # Create HMAC signature
        signature = self._create_signature(webhook.secret, payload)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-ID': str(webhook.id),
            'X-Webhook-Event': event_type,
            'X-Webhook-Timestamp': timezone.now().isoformat(),
        }
        
        # Send webhook
        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        # Record webhook event
        WebhookEvent.objects.create(
            webhook=webhook,
            event_type=event_type,
            status='success',
            response_status_code=response.status_code,
            attempt=self.request.retries + 1
        )
        
        webhook.last_triggered = timezone.now()
        webhook.save()
        
        logger.info(f"Webhook {webhook_id} sent successfully for event {event_type}")
        
    except requests.RequestException as e:
        logger.error(f"Webhook {webhook_id} delivery failed: {str(e)}")
        
        retry_count = self.request.retries
        countdown = INITIAL_RETRY_DELAY * (2 ** retry_count)
        
        try:
            WebhookEvent.objects.create(
                webhook_id=webhook_id,
                event_type=event_type,
                status='failed',
                error_message=str(e),
                attempt=retry_count + 1
            )
        except:
            pass
        
        raise self.retry(countdown=countdown, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error sending webhook: {str(e)}")
        raise
    
    @staticmethod
    def _create_signature(secret, payload):
        """Create HMAC SHA256 signature"""
        import json
        message = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()


@shared_task(bind=True, max_retries=MAX_RETRIES)
def process_transaction_webhook(self, transaction_id, idempotency_key=None):
    """Process transaction and send webhooks with idempotency"""
    try:
        if idempotency_key:
            cache_key = f"webhook_processed:{transaction_id}:{idempotency_key}"
            if cache.get(cache_key):
                logger.info(f"Webhook already processed for {transaction_id} with key {idempotency_key}")
                return
        
        transaction = Transaction.objects.get(id=transaction_id)
        user_webhooks = Webhook.objects.filter(user=transaction.user, is_active=True)
        
        # Filter webhooks by event type
        event_type = f"payment.{transaction.status}"
        
        for webhook in user_webhooks:
            if event_type in webhook.event_types:
                payload = {
                    'event': event_type,
                    'timestamp': timezone.now().isoformat(),
                    'data': {
                        'transaction_id': str(transaction.id),
                        'amount': float(transaction.amount),
                        'currency': transaction.currency,
                        'status': transaction.status,
                        'provider': transaction.provider,
                        'reference': transaction.reference,
                        'customer_email': transaction.customer_email,
                        'idempotency_key': transaction.idempotency_key,
                    }
                }
                
                # Send webhook asynchronously
                send_webhook.delay(str(webhook.id), event_type, payload)
        
        # Mark webhook as processed
        if idempotency_key:
            cache.set(cache_key, True, 86400)  # Cache for 24 hours
                
    except Transaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")
    except Exception as e:
        logger.error(f"Error processing transaction webhook: {str(e)}")
        # Retry on error
        if self.request.retries < MAX_RETRIES:
            countdown = INITIAL_RETRY_DELAY * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=e)


@shared_task(bind=True, max_retries=3)
def retry_failed_payment(self, transaction_id):
    """
    Retry a failed payment transaction.
    Only retries if network error, not for invalid card/auth errors.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Only retry if status is pending or failed
        if transaction.status not in ['pending', 'failed']:
            logger.info(f"Transaction {transaction_id} already {transaction.status}")
            return
        
        from .payment_service import PaymentService
        payment_service = PaymentService()
        
        # Attempt to retry payment verification
        if transaction.provider == 'stripe':
            result = payment_service.confirm_payment_intent(
                transaction.reference,
                transaction.stripe_payment_method_id
            )
            
            if result['success']:
                transaction.status = 'completed'
                transaction.provider_response = result
                transaction.save()
                
                # Process webhook with idempotency
                process_transaction_webhook.delay(
                    str(transaction.id),
                    transaction.idempotency_key
                )
                
                logger.info(f"Transaction {transaction_id} successfully retried")
            else:
                # Retry on network errors only
                if result.get('retry'):
                    retry_count = self.request.retries
                    countdown = 60 * (2 ** retry_count)  # Exponential backoff
                    raise self.retry(countdown=countdown)
        
    except Transaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")
    except Exception as e:
        logger.error(f"Error retrying payment: {str(e)}")
        if self.request.retries < 3:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=e)


@shared_task
def process_kyc_webhook(kyc_verification_id, event_type):
    """Process KYC and send webhooks"""
    from .models import KYCVerification
    
    try:
        kyc = KYCVerification.objects.get(id=kyc_verification_id)
        user_webhooks = Webhook.objects.filter(user=kyc.user, is_active=True)
        
        for webhook in user_webhooks:
            if event_type in webhook.event_types:
                payload = {
                    'event': event_type,
                    'timestamp': timezone.now().isoformat(),
                    'data': {
                        'kyc_id': str(kyc.id),
                        'verification_type': kyc.verification_type,
                        'status': kyc.status,
                        'provider': kyc.provider,
                    }
                }
                
                send_webhook.delay(str(webhook.id), event_type, payload)
                
    except Exception as e:
        logger.error(f"Error processing KYC webhook: {str(e)}")


@shared_task
def generate_monthly_invoices():
    """Generate monthly invoices for all users"""
    from django.contrib.auth.models import User
    from .billing_service import BillingService
    
    try:
        # Get all users with active subscriptions
        users = User.objects.filter(subscription__status='active')
        
        billing_period_end = timezone.now().date()
        billing_period_start = (timezone.now() - timedelta(days=30)).date()
        
        for user in users:
            try:
                BillingService.generate_invoice(user, billing_period_start, billing_period_end)
            except Exception as e:
                logger.error(f"Failed to generate invoice for {user.email}: {str(e)}")
        
        logger.info(f"Generated invoices for {users.count()} users")
        
    except Exception as e:
        logger.error(f"Error generating monthly invoices: {str(e)}")


@shared_task
def check_overdue_invoices():
    """Check and mark overdue invoices"""
    try:
        today = timezone.now().date()
        
        overdue_invoices = Invoice.objects.filter(
            status__in=['issued'],
            due_date__lt=today
        )
        
        overdue_invoices.update(status='overdue')
        
        logger.info(f"Marked {overdue_invoices.count()} invoices as overdue")
        
    except Exception as e:
        logger.error(f"Error checking overdue invoices: {str(e)}")


@shared_task
def cleanup_old_logs():
    """Clean up old API logs (keep only 90 days)"""
    try:
        cutoff_date = timezone.now() - timedelta(days=90)
        
        deleted_count, _ = APILog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Deleted {deleted_count} old API logs")
        
    except Exception as e:
        logger.error(f"Error cleaning up logs: {str(e)}")


@shared_task
def retry_failed_webhooks():
    """Retry failed webhook deliveries with smart backoff"""
    try:
        from .models import WebhookEvent
        
        failed_events = WebhookEvent.objects.filter(
            status='failed',
            attempt__lt=MAX_RETRIES,
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        for event in failed_events:
            # Recreate webhook payload and retry with backoff
            webhook = event.webhook
            payload = event.payload
            
            # Exponential backoff based on attempt count
            countdown = INITIAL_RETRY_DELAY * (2 ** (event.attempt - 1))
            
            send_webhook.apply_async(
                args=[str(webhook.id), event.event_type, payload],
                countdown=countdown
            )
            
        logger.info(f"Scheduled retry for {failed_events.count()} failed webhooks")
        
    except Exception as e:
        logger.error(f"Error retrying failed webhooks: {str(e)}")
