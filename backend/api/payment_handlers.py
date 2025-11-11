import requests
import hmac
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from .models import Transaction, PaymentProvider
from django.db import transaction as db_transaction


class PaymentHandler:
    """Base payment handler for all providers"""
    
    def __init__(self, provider_name):
        self.provider_name = provider_name
    
    def verify_signature(self, payload, signature, secret):
        """Verify webhook signature"""
        raise NotImplementedError
    
    def process_webhook(self, data):
        """Process webhook from payment provider"""
        raise NotImplementedError
    
    def check_idempotency(self, idempotency_key):
        """Check if request with same idempotency key was already processed"""
        from .models import Transaction
        if not idempotency_key:
            return None
        
        transaction = Transaction.objects.filter(
            idempotency_key=idempotency_key
        ).first()
        return transaction


class PaystackHandler(PaymentHandler):
    """Paystack payment handler"""
    
    def __init__(self):
        super().__init__('paystack')
    
    def verify_signature(self, payload, signature, secret=None):
        """Verify Paystack webhook signature"""
        secret = secret or settings.PAYSTACK_SECRET_KEY
        computed = hmac.new(secret.encode(), payload, hashlib.sha512).hexdigest()
        return computed == signature
    
    def process_webhook(self, data):
        """Process Paystack webhook"""
        reference = data.get('reference')
        status = 'completed' if data.get('status') == 'success' else 'failed'
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=reference).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                trans.save()
                return trans
        return None
    
    def initiate_payment(self, amount, email, reference, callback_url):
        """Initiate Paystack payment"""
        headers = {'Authorization': f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        payload = {
            'amount': int(amount * 100),
            'email': email,
            'reference': reference,
            'callback_url': callback_url,
        }
        
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=headers,
            json=payload
        )
        return response.json()


class FlutterwaveHandler(PaymentHandler):
    """Flutterwave payment handler"""
    
    def __init__(self):
        super().__init__('flutterwave')
    
    def verify_signature(self, payload, signature, secret=None):
        """Verify Flutterwave webhook signature"""
        secret = secret or settings.FLUTTERWAVE_SECRET_KEY
        computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return computed == signature
    
    def process_webhook(self, data):
        """Process Flutterwave webhook"""
        reference = data.get('txRef')
        status = 'completed' if data.get('status') == 'successful' else 'failed'
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=reference).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                trans.save()
                return trans
        return None
    
    def initiate_payment(self, amount, email, reference, callback_url):
        """Initiate Flutterwave payment"""
        headers = {'Authorization': f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
        payload = {
            'amount': amount,
            'email': email,
            'tx_ref': reference,
            'redirect_url': callback_url,
        }
        
        response = requests.post(
            'https://api.flutterwave.com/v3/payments',
            headers=headers,
            json=payload
        )
        return response.json()


class StripeHandler(PaymentHandler):
    """Stripe payment handler with card tokenization"""
    
    def __init__(self):
        super().__init__('stripe')
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
    
    def verify_signature(self, payload, signature, secret=None):
        """Verify Stripe webhook signature"""
        secret = secret or settings.STRIPE_WEBHOOK_SECRET
        try:
            import stripe
            stripe.api_key = settings.STRIPE_API_KEY
            event = stripe.Webhook.construct_event(payload, signature, secret)
            return True
        except Exception:
            return False
    
    def process_webhook(self, data):
        """Process Stripe webhook"""
        intent_id = data.get('id')
        status = 'completed' if data.get('status') == 'succeeded' else 'failed'
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=intent_id).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                trans.save()
                return trans
        return None
    
    def create_payment_intent_with_tokenization(self, amount, customer_email, currency='usd', save_card=False):
        """Create payment intent with tokenization (no card storage)"""
        import stripe
        
        try:
            # Never create customer record if save_card is False
            customer_params = {} if not save_card else {
                'email': customer_email,
                'description': f'PayBridge customer {customer_email}',
            }
            
            customer_id = None
            if save_card:
                customer = stripe.Customer.create(**customer_params)
                customer_id = customer.id
            
            # Create payment intent with payment method (tokenized)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                description=f'Payment via PayBridge - {customer_email}',
                customer=customer_id,  # None if not saving card
                statement_descriptor='PAYBRIDGE',
            )
            
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'customer_id': customer_id,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_webhook_with_idempotency(self, data, idempotency_key=None):
        """Process Stripe webhook with idempotency"""
        from .models import Transaction
        
        # Check if already processed
        if idempotency_key:
            existing = Transaction.objects.filter(
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing
        
        intent_id = data.get('id')
        status = 'completed' if data.get('status') == 'succeeded' else 'failed'
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=intent_id).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                if idempotency_key:
                    trans.idempotency_key = idempotency_key
                trans.save()
                return trans
        return None


class ChapaHandler(PaymentHandler):
    """Chapa payment handler"""
    
    def __init__(self):
        super().__init__('chapa')
    
    def verify_signature(self, payload, signature, secret=None):
        """Verify Chapa webhook signature"""
        secret = secret or settings.CHAPA_API_KEY
        computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return computed == signature
    
    def process_webhook(self, data):
        """Process Chapa webhook"""
        reference = data.get('tx_ref')
        status = 'completed' if data.get('status') == 'success' else 'failed'
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=reference).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                trans.save()
                return trans
        return None


class MonoHandler(PaymentHandler):
    """Mono payment handler"""
    
    def __init__(self):
        super().__init__('mono')
    
    def verify_signature(self, payload, signature, secret=None):
        """Verify Mono webhook signature"""
        secret = secret or getattr(settings, 'MONO_API_KEY', '')
        if not secret:
            return True  # Skip verification if no secret configured
        computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return computed == signature
    
    def process_webhook(self, data):
        """Process Mono webhook"""
        reference = data.get('reference') or data.get('id')
        status_map = {
            'successful': 'completed',
            'success': 'completed',
            'failed': 'failed',
            'pending': 'pending',
        }
        status = status_map.get(data.get('status', '').lower(), 'failed')
        
        with db_transaction.atomic():
            trans = Transaction.objects.filter(reference=reference).first()
            if trans:
                trans.status = status
                trans.provider_response = data
                trans.save()
                return trans
        return None
    
    def initiate_payment(self, amount, email, reference, callback_url):
        """Initiate Mono payment"""
        api_key = getattr(settings, 'MONO_API_KEY', '')
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json',
        }
        payload = {
            'amount': amount,
            'email': email,
            'reference': reference,
            'callback_url': callback_url,
        }
        
        response = requests.post(
            'https://api.withmono.com/v1/payments/initiate',
            headers=headers,
            json=payload
        )
        return response.json()


def get_payment_handler(provider_name):
    """Factory function to get payment handler"""
    handlers = {
        'paystack': PaystackHandler,
        'flutterwave': FlutterwaveHandler,
        'stripe': StripeHandler,
        'chapa': ChapaHandler,
        'mono': MonoHandler,
    }
    handler_class = handlers.get(provider_name)
    if not handler_class:
        raise ValueError(f"Unknown payment provider: {provider_name}")
    return handler_class()
