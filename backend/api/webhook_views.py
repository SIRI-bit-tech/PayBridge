from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Webhook, Transaction, AuditLog
from .payment_handlers import get_payment_handler
import json


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Paystack payment webhook endpoint"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        
        handler = get_payment_handler('paystack')
        if not handler.verify_signature(payload, signature):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        event = data.get('event')
        
        if event == 'charge.success':
            trans_data = data.get('data', {})
            handler.process_webhook(trans_data)
            
            # Trigger user webhooks
            transaction = Transaction.objects.filter(
                reference=trans_data.get('reference')
            ).first()
            
            if transaction:
                webhooks = Webhook.objects.filter(
                    user=transaction.user,
                    is_active=True,
                    event_types__contains='payment.completed'
                )
                for webhook in webhooks:
                    trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
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
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        handler.process_webhook(data)
        
        transaction = Transaction.objects.filter(
            reference=data.get('txRef')
        ).first()
        
        if transaction:
            webhooks = Webhook.objects.filter(
                user=transaction.user,
                is_active=True,
                event_types__contains='payment.completed'
            )
            for webhook in webhooks:
                trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
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
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        event_type = data.get('type')
        
        if event_type == 'payment_intent.succeeded':
            event_data = data.get('data', {}).get('object', {})
            handler.process_webhook(event_data)
            
            transaction = Transaction.objects.filter(
                reference=event_data.get('id')
            ).first()
            
            if transaction:
                webhooks = Webhook.objects.filter(
                    user=transaction.user,
                    is_active=True,
                    event_types__contains='payment.completed'
                )
                for webhook in webhooks:
                    trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
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
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(payload)
        handler.process_webhook(data)
        
        transaction = Transaction.objects.filter(
            reference=data.get('tx_ref')
        ).first()
        
        if transaction:
            webhooks = Webhook.objects.filter(
                user=transaction.user,
                is_active=True,
                event_types__contains='payment.completed'
            )
            for webhook in webhooks:
                trigger_webhook(webhook, transaction)
        
        return Response({'status': 'success'})
    except Exception as e:
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
