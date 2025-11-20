"""
Webhook Receiver - Handles incoming webhooks from payment/KYC providers
Validates signatures, deduplicates, and queues for processing
"""
import logging
import hmac
import hashlib
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .webhook_models import WebhookEvent
from .webhook_tasks import process_provider_webhook

logger = logging.getLogger(__name__)


def verify_paystack_signature(payload, signature):
    """Verify Paystack webhook signature"""
    secret = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
    computed = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


def verify_flutterwave_signature(payload, signature):
    """Verify Flutterwave webhook signature"""
    secret = getattr(settings, 'FLUTTERWAVE_SECRET_HASH', '')
    return hmac.compare_digest(secret, signature)


def verify_stripe_signature(payload, signature):
    """Verify Stripe webhook signature"""
    import stripe
    secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    try:
        stripe.Webhook.construct_event(
            payload, signature, secret
        )
        return True
    except Exception as e:
        logger.error(f"Stripe signature verification failed: {str(e)}")
        return False


def verify_mono_signature(payload, signature):
    """Verify Mono webhook signature"""
    secret = getattr(settings, 'MONO_SECRET_KEY', '')
    computed = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


def normalize_paystack_event(data):
    """Convert Paystack event to canonical format"""
    event = data.get('event', '')
    event_data = data.get('data', {})
    
    # Map Paystack events to canonical events
    event_mapping = {
        'charge.success': 'payment.completed',
        'charge.failed': 'payment.failed',
        'transfer.success': 'transfer.completed',
        'transfer.failed': 'transfer.failed',
        'subscription.create': 'subscription.created',
        'subscription.disable': 'subscription.cancelled',
    }
    
    canonical_type = event_mapping.get(event, f'paystack.{event}')
    provider_event_id = event_data.get('id') or event_data.get('reference', '')
    
    return canonical_type, provider_event_id


def normalize_flutterwave_event(data):
    """Convert Flutterwave event to canonical format"""
    event = data.get('event', '')
    event_data = data.get('data', {})
    
    event_mapping = {
        'charge.completed': 'payment.completed',
        'charge.failed': 'payment.failed',
        'transfer.completed': 'transfer.completed',
        'transfer.failed': 'transfer.failed',
    }
    
    canonical_type = event_mapping.get(event, f'flutterwave.{event}')
    provider_event_id = event_data.get('id') or event_data.get('tx_ref', '')
    
    return canonical_type, str(provider_event_id)


def normalize_stripe_event(data):
    """Convert Stripe event to canonical format"""
    event_type = data.get('type', '')
    event_data = data.get('data', {}).get('object', {})
    
    event_mapping = {
        'payment_intent.succeeded': 'payment.completed',
        'payment_intent.payment_failed': 'payment.failed',
        'charge.succeeded': 'payment.completed',
        'charge.failed': 'payment.failed',
        'customer.subscription.created': 'subscription.created',
        'customer.subscription.updated': 'subscription.updated',
        'customer.subscription.deleted': 'subscription.cancelled',
        'payout.paid': 'transfer.completed',
        'payout.failed': 'transfer.failed',
    }
    
    canonical_type = event_mapping.get(event_type, f'stripe.{event_type}')
    provider_event_id = data.get('id', '')
    
    return canonical_type, provider_event_id


def normalize_mono_event(data):
    """Convert Mono event to canonical format"""
    event = data.get('event', '')
    event_data = data.get('data', {})
    
    event_mapping = {
        'mono.events.account_linked': 'kyc.verified',
        'mono.events.account_updated': 'kyc.updated',
        'mono.events.reauthorisation_required': 'kyc.reauth_required',
    }
    
    canonical_type = event_mapping.get(event, f'mono.{event}')
    provider_event_id = event_data.get('id', '')
    
    return canonical_type, provider_event_id


@csrf_exempt
@require_http_methods(["POST"])
def webhook_paystack(request):
    """Receive and validate Paystack webhooks"""
    try:
        signature = request.headers.get('X-Paystack-Signature', '')
        if not signature:
            logger.warning("Paystack webhook received without signature")
            return JsonResponse({'error': 'No signature provided'}, status=400)
        
        # Verify signature
        signature_valid = verify_paystack_signature(request.body, signature)
        
        if not signature_valid:
            logger.warning("Paystack webhook signature verification failed")
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Parse payload
        data = json.loads(request.body)
        
        # Normalize event
        canonical_type, provider_event_id = normalize_paystack_event(data)
        
        if not provider_event_id:
            logger.error("Paystack webhook missing event ID")
            return JsonResponse({'error': 'Missing event ID'}, status=400)
        
        # Check for duplicate (idempotency)
        existing = WebhookEvent.objects.filter(
            provider='paystack',
            provider_event_id=provider_event_id
        ).first()
        
        if existing:
            logger.info(f"Duplicate Paystack webhook: {provider_event_id}")
            return JsonResponse({'status': 'duplicate', 'event_id': str(existing.id)})
        
        # Store webhook event
        webhook_event = WebhookEvent.objects.create(
            provider='paystack',
            provider_event_id=provider_event_id,
            canonical_event_type=canonical_type,
            raw_payload=data,
            signature_valid=True,
            processing_status='pending'
        )
        
        # Queue for async processing
        process_provider_webhook.delay(str(webhook_event.id))
        
        logger.info(f"Paystack webhook received: {canonical_type} - {provider_event_id}")
        
        return JsonResponse({
            'status': 'received',
            'event_id': str(webhook_event.id)
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Paystack webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Paystack webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_flutterwave(request):
    """Receive and validate Flutterwave webhooks"""
    try:
        signature = request.headers.get('verif-hash', '')
        if not signature:
            logger.warning("Flutterwave webhook received without signature")
            return JsonResponse({'error': 'No signature provided'}, status=400)
        
        signature_valid = verify_flutterwave_signature(request.body, signature)
        
        if not signature_valid:
            logger.warning("Flutterwave webhook signature verification failed")
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        data = json.loads(request.body)
        canonical_type, provider_event_id = normalize_flutterwave_event(data)
        
        if not provider_event_id:
            logger.error("Flutterwave webhook missing event ID")
            return JsonResponse({'error': 'Missing event ID'}, status=400)
        
        existing = WebhookEvent.objects.filter(
            provider='flutterwave',
            provider_event_id=provider_event_id
        ).first()
        
        if existing:
            logger.info(f"Duplicate Flutterwave webhook: {provider_event_id}")
            return JsonResponse({'status': 'duplicate', 'event_id': str(existing.id)})
        
        webhook_event = WebhookEvent.objects.create(
            provider='flutterwave',
            provider_event_id=provider_event_id,
            canonical_event_type=canonical_type,
            raw_payload=data,
            signature_valid=True,
            processing_status='pending'
        )
        
        process_provider_webhook.delay(str(webhook_event.id))
        
        logger.info(f"Flutterwave webhook received: {canonical_type} - {provider_event_id}")
        
        return JsonResponse({
            'status': 'received',
            'event_id': str(webhook_event.id)
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Flutterwave webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Flutterwave webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_stripe(request):
    """Receive and validate Stripe webhooks"""
    try:
        signature = request.headers.get('Stripe-Signature', '')
        if not signature:
            logger.warning("Stripe webhook received without signature")
            return JsonResponse({'error': 'No signature provided'}, status=400)
        
        signature_valid = verify_stripe_signature(request.body, signature)
        
        if not signature_valid:
            logger.warning("Stripe webhook signature verification failed")
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        data = json.loads(request.body)
        canonical_type, provider_event_id = normalize_stripe_event(data)
        
        if not provider_event_id:
            logger.error("Stripe webhook missing event ID")
            return JsonResponse({'error': 'Missing event ID'}, status=400)
        
        existing = WebhookEvent.objects.filter(
            provider='stripe',
            provider_event_id=provider_event_id
        ).first()
        
        if existing:
            logger.info(f"Duplicate Stripe webhook: {provider_event_id}")
            return JsonResponse({'status': 'duplicate', 'event_id': str(existing.id)})
        
        webhook_event = WebhookEvent.objects.create(
            provider='stripe',
            provider_event_id=provider_event_id,
            canonical_event_type=canonical_type,
            raw_payload=data,
            signature_valid=True,
            processing_status='pending'
        )
        
        process_provider_webhook.delay(str(webhook_event.id))
        
        logger.info(f"Stripe webhook received: {canonical_type} - {provider_event_id}")
        
        return JsonResponse({
            'status': 'received',
            'event_id': str(webhook_event.id)
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Stripe webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_mono(request):
    """Receive and validate Mono webhooks"""
    try:
        signature = request.headers.get('X-Mono-Signature', '')
        if not signature:
            logger.warning("Mono webhook received without signature")
            return JsonResponse({'error': 'No signature provided'}, status=400)
        
        signature_valid = verify_mono_signature(request.body, signature)
        
        if not signature_valid:
            logger.warning("Mono webhook signature verification failed")
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        data = json.loads(request.body)
        canonical_type, provider_event_id = normalize_mono_event(data)
        
        if not provider_event_id:
            logger.error("Mono webhook missing event ID")
            return JsonResponse({'error': 'Missing event ID'}, status=400)
        
        existing = WebhookEvent.objects.filter(
            provider='mono',
            provider_event_id=provider_event_id
        ).first()
        
        if existing:
            logger.info(f"Duplicate Mono webhook: {provider_event_id}")
            return JsonResponse({'status': 'duplicate', 'event_id': str(existing.id)})
        
        webhook_event = WebhookEvent.objects.create(
            provider='mono',
            provider_event_id=provider_event_id,
            canonical_event_type=canonical_type,
            raw_payload=data,
            signature_valid=True,
            processing_status='pending'
        )
        
        process_provider_webhook.delay(str(webhook_event.id))
        
        logger.info(f"Mono webhook received: {canonical_type} - {provider_event_id}")
        
        return JsonResponse({
            'status': 'received',
            'event_id': str(webhook_event.id)
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Mono webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Mono webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
