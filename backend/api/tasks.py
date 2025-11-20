from celery import shared_task
import logging
import requests
import hmac
import hashlib
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from .models import Transaction, APILog, Invoice, UsageMetric
from .exceptions import WebhookDeliveryFailed
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 300  # 5 minutes


# send_webhook task moved to webhook_tasks.py


# process_transaction_webhook moved to webhook_tasks.py with improved logic


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


# process_kyc_webhook moved to webhook_tasks.py


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
def update_api_key_last_used(api_key_id):
    """Update API key last_used timestamp asynchronously"""
    from .models import APIKey
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    try:
        api_key = APIKey.objects.get(id=api_key_id)
        api_key.last_used = timezone.now()
        api_key.save(update_fields=['last_used'])
        
        # Broadcast real-time update
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"api_keys_{api_key.user.id}",
                {
                    'type': 'api_key_used',
                    'data': {
                        'id': str(api_key.id),
                        'last_used': api_key.last_used.isoformat(),
                    }
                }
            )
        
        logger.debug(f"Updated last_used for API key {api_key_id}")
        
    except APIKey.DoesNotExist:
        logger.warning(f"API key {api_key_id} not found")
    except Exception as e:
        logger.error(f"Error updating API key last_used: {str(e)}")


# retry_failed_webhooks moved to webhook_tasks.py with improved retry logic
