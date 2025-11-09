from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Webhook, Transaction, AuditLog, WebhookEvent
from .payment_handlers import get_payment_handler
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import logging

logger = logging.getLogger(__name__)


def broadcast_to_user(user_id, event_type, data):
    """Broadcast event to user's WebSocket connection"""
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"dashboard_{user_id}",
            {
                "type": event_type,
                "data": data
            }
        )
        logger.info(f"Broadcasted {event_type} to user {user_id}")


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Paystack payment webhook endpoint"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        
        handler = get_payment_handler('paystack')
        if not handler.verify_signature(payload, signature):
            logger.warning("Invalid Paystack webhook signature")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        event = data.get('event')
        
        logger.info(f"Received Paystack webhook: {event}")
        
        if event == 'charge.success':
            trans_data = data.get('data', {})
            transaction = handler.process_webhook(trans_data)
            
            if transaction:
                # Log webhook event
                WebhookEvent.objects.create(
                    webhook=None,
                    event_type='payment.completed',
                    payload=data,
                    status='success'
                )
                
                # Broadcast to user's dashboard
                broadcast_to_user(
                    transaction.user.id,
                    'transaction_update',
                    {
                        'id': str(transaction.id),
                        'reference': transaction.reference,
                        'amount': str(transaction.amount),
                        'currency': transaction.currency,
                        'status': transaction.status,
                        'provider': transaction.provider,
                        'created_at': transaction.created_at.isoformat(),
                        'message': 'Payment completed successfully'
                    }
                )
                
                # Trigger user webhooks
                webhooks = Webhook.objects.filter(
                    user=transaction.user,
                    is_active=True,
                    event_types__contains='payment.completed'
                )
                for webhook in webhooks:
                    trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
        logger.error(f"Paystack webhook error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def flutterwave_webhook(request):
    """Flutterwave payment webhook endpoint"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_VERIF_HASH')
        
        handler = get_payment_handler('flutterwave')
        if not handler.verify_signature(payload, signature):
            logger.warning("Invalid Flutterwave webhook signature")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        logger.info(f"Received Flutterwave webhook: {data.get('event')}")
        
        transaction = handler.process_webhook(data)
        
        if transaction:
            # Log webhook event
            WebhookEvent.objects.create(
                webhook=None,
                event_type='payment.completed',
                payload=data,
                status='success'
            )
            
            # Broadcast to user's dashboard
            broadcast_to_user(
                transaction.user.id,
                'transaction_update',
                {
                    'id': str(transaction.id),
                    'reference': transaction.reference,
                    'amount': str(transaction.amount),
                    'currency': transaction.currency,
                    'status': transaction.status,
                    'provider': transaction.provider,
                    'created_at': transaction.created_at.isoformat(),
                    'message': 'Payment completed successfully'
                }
            )
            
            # Trigger user webhooks
            webhooks = Webhook.objects.filter(
                user=transaction.user,
                is_active=True,
                event_types__contains='payment.completed'
            )
            for webhook in webhooks:
                trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
        logger.error(f"Flutterwave webhook error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Stripe payment webhook endpoint"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        handler = get_payment_handler('stripe')
        if not handler.verify_signature(payload, signature):
            logger.warning("Invalid Stripe webhook signature")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        event_type = data.get('type')
        
        logger.info(f"Received Stripe webhook: {event_type}")
        
        if event_type == 'payment_intent.succeeded':
            event_data = data.get('data', {}).get('object', {})
            transaction = handler.process_webhook(event_data)
            
            if transaction:
                # Log webhook event
                WebhookEvent.objects.create(
                    webhook=None,
                    event_type='payment.completed',
                    payload=data,
                    status='success'
                )
                
                # Broadcast to user's dashboard
                broadcast_to_user(
                    transaction.user.id,
                    'transaction_update',
                    {
                        'id': str(transaction.id),
                        'reference': transaction.reference,
                        'amount': str(transaction.amount),
                        'currency': transaction.currency,
                        'status': transaction.status,
                        'provider': transaction.provider,
                        'created_at': transaction.created_at.isoformat(),
                        'message': 'Payment completed successfully'
                    }
                )
                
                # Trigger user webhooks
                webhooks = Webhook.objects.filter(
                    user=transaction.user,
                    is_active=True,
                    event_types__contains='payment.completed'
                )
                for webhook in webhooks:
                    trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def chapa_webhook(request):
    """Chapa payment webhook endpoint"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_X_CHAPA_SIGNATURE')
        
        handler = get_payment_handler('chapa')
        if not handler.verify_signature(payload, signature):
            logger.warning("Invalid Chapa webhook signature")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        logger.info(f"Received Chapa webhook")
        
        transaction = handler.process_webhook(data)
        
        if transaction:
            # Log webhook event
            WebhookEvent.objects.create(
                webhook=None,
                event_type='payment.completed',
                payload=data,
                status='success'
            )
            
            # Broadcast to user's dashboard
            broadcast_to_user(
                transaction.user.id,
                'transaction_update',
                {
                    'id': str(transaction.id),
                    'reference': transaction.reference,
                    'amount': str(transaction.amount),
                    'currency': transaction.currency,
                    'status': transaction.status,
                    'provider': transaction.provider,
                    'created_at': transaction.created_at.isoformat(),
                    'message': 'Payment completed successfully'
                }
            )
            
            # Trigger user webhooks
            webhooks = Webhook.objects.filter(
                user=transaction.user,
                is_active=True,
                event_types__contains='payment.completed'
            )
            for webhook in webhooks:
                trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
        logger.error(f"Chapa webhook error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def trigger_webhook(webhook, transaction):
    """Trigger user webhook with transaction data"""
    import requests
    
    payload = {
        'event': 'payment.completed',
        'transaction': {
            'id': str(transaction.id),
            'reference': transaction.reference,
            'amount': float(transaction.amount),
            'currency': transaction.currency,
            'status': transaction.status,
            'timestamp': transaction.created_at.isoformat(),
        }
    }
    
    try:
        requests.post(webhook.url, json=payload, timeout=10)
        webhook.last_triggered = __import__('django.utils.timezone', fromlist=['now']).now()
        webhook.save()
    except Exception as e:
        webhook.retry_count += 1
        webhook.save()
