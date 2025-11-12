"""
Payment Provider Integrations (Paystack, Flutterwave, Stripe)
"""
import requests
import stripe
import logging
import uuid
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymentProviderBase:
    """Base class for payment providers"""
    
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or self.get_default_secret_key()
    
    def get_default_secret_key(self):
        """Override in subclasses"""
        raise NotImplementedError
    
    def create_payment_intent(self, amount, currency, email, metadata=None):
        """Create a payment intent"""
        raise NotImplementedError
    
    def verify_payment(self, reference):
        """Verify a payment"""
        raise NotImplementedError
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature"""
        raise NotImplementedError


class PaystackProvider(PaymentProviderBase):
    """Paystack payment provider"""
    
    BASE_URL = "https://api.paystack.co"
    
    def get_default_secret_key(self):
        return settings.PAYSTACK_SECRET_KEY
    
    def create_payment_intent(self, amount, currency, email, metadata=None):
        """Initialize Paystack transaction"""
        try:
            # Paystack expects amount in kobo (smallest currency unit)
            amount_in_kobo = int(Decimal(str(amount)) * 100)
            
            reference = f"ps_{uuid.uuid4().hex[:20]}"
            
            payload = {
                "email": email,
                "amount": amount_in_kobo,
                "currency": currency,
                "reference": reference,
                "metadata": metadata or {},
            }
            
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(
                f"{self.BASE_URL}/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'payment_intent': reference,
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code'],
                    'reference': reference,
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Failed to initialize payment')
                }
                
        except Exception as e:
            logger.error(f"Paystack payment intent error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, reference):
        """Verify Paystack payment"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
            }
            
            response = requests.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Safely extract payload - Paystack may return data as None when status is false
            payload = data.get('data') or {}
            
            # Check both that status is True and payload is truthy
            if data.get('status') and payload and payload.get('status') == 'success':
                # Safely get amount and convert to Decimal
                amount_kobo = payload.get('amount')
                amount = Decimal(str(amount_kobo)) / 100 if amount_kobo else Decimal('0')
                
                return {
                    'success': True,
                    'amount': amount,
                    'currency': payload.get('currency', 'NGN'),
                    'reference': payload.get('reference', reference),
                    'status': 'success',
                    'raw_response': payload
                }
            else:
                return {
                    'success': False,
                    'status': payload.get('status', 'failed') if payload else 'failed',
                    'error': data.get('message', 'Payment verification failed')
                }
                
        except Exception as e:
            logger.error(f"Paystack verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def verify_webhook_signature(self, payload, signature):
        """Verify Paystack webhook signature"""
        import hmac
        import hashlib
        
        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_signature = hmac.new(secret, payload, hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed_signature, signature)


class FlutterwaveProvider(PaymentProviderBase):
    """Flutterwave payment provider"""
    
    BASE_URL = "https://api.flutterwave.com/v3"
    
    def get_default_secret_key(self):
        return settings.FLUTTERWAVE_SECRET_KEY
    
    def create_payment_intent(self, amount, currency, email, metadata=None):
        """Initialize Flutterwave payment"""
        try:
            reference = f"fw_{uuid.uuid4().hex[:20]}"
            
            payload = {
                "tx_ref": reference,
                "amount": str(amount),
                "currency": currency,
                "redirect_url": f"{settings.FRONTEND_URL}/billing/verify",
                "customer": {
                    "email": email,
                },
                "customizations": {
                    "title": "PayBridge Subscription",
                    "description": "Subscription payment",
                },
                "meta": metadata or {},
            }
            
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(
                f"{self.BASE_URL}/payments",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'payment_intent': reference,
                    'authorization_url': data['data']['link'],
                    'reference': reference,
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Failed to initialize payment')
                }
                
        except Exception as e:
            logger.error(f"Flutterwave payment intent error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, reference):
        """Verify Flutterwave payment"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
            }
            
            response = requests.get(
                f"{self.BASE_URL}/transactions/verify_by_reference?tx_ref={reference}",
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Safely extract payload - Flutterwave may return error without data object
            payload = data.get('data')
            
            # Check both that status is 'success' and payload exists
            if data.get('status') == 'success' and payload and payload.get('status') == 'successful':
                # Safely get amount and convert to Decimal
                amount_value = payload.get('amount')
                amount = Decimal(str(amount_value)) if amount_value else Decimal('0')
                
                return {
                    'success': True,
                    'amount': amount,
                    'currency': payload.get('currency', 'NGN'),
                    'reference': payload.get('tx_ref', reference),
                    'status': 'success',
                    'raw_response': payload
                }
            else:
                return {
                    'success': False,
                    'status': payload.get('status', 'failed') if payload else data.get('status', 'failed'),
                    'error': data.get('message', 'Payment verification failed')
                }
                
        except Exception as e:
            logger.error(f"Flutterwave verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload, signature):
        """Verify Flutterwave webhook signature"""
        # Flutterwave uses a secret hash for verification
        secret_hash = settings.FLUTTERWAVE_SECRET_HASH
        return signature == secret_hash


class StripeProvider(PaymentProviderBase):
    """Stripe payment provider"""
    
    def get_default_secret_key(self):
        return settings.STRIPE_SECRET_KEY
    
    def __init__(self, secret_key=None):
        super().__init__(secret_key)
        stripe.api_key = self.secret_key
    
    def create_payment_intent(self, amount, currency, email, metadata=None):
        """Create Stripe payment intent"""
        try:
            # Stripe expects amount in cents
            amount_in_cents = int(Decimal(str(amount)) * 100)
            
            reference = f"stripe_{uuid.uuid4().hex[:20]}"
            
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=currency.lower(),
                metadata={
                    'reference': reference,
                    **(metadata or {})
                },
                receipt_email=email,
            )
            
            return {
                'success': True,
                'payment_intent': intent.id,
                'client_secret': intent.client_secret,
                'reference': reference,
            }
                
        except Exception as e:
            logger.error(f"Stripe payment intent error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_intent_id):
        """Verify Stripe payment"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                return {
                    'success': True,
                    'amount': Decimal(str(intent.amount)) / 100,
                    'currency': intent.currency.upper(),
                    'reference': intent.metadata.get('reference', payment_intent_id),
                    'status': 'success',
                    'raw_response': dict(intent)
                }
            else:
                return {
                    'success': False,
                    'status': intent.status,
                    'error': f'Payment status: {intent.status}'
                }
                
        except Exception as e:
            logger.error(f"Stripe verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload, signature):
        """Verify Stripe webhook signature"""
        try:
            webhook_secret = settings.STRIPE_WEBHOOK_SECRET
            stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True
        except Exception as e:
            logger.error(f"Stripe webhook verification failed: {str(e)}")
            return False


def get_payment_provider(provider_name, secret_key=None):
    """Factory function to get payment provider instance"""
    providers = {
        'paystack': PaystackProvider,
        'flutterwave': FlutterwaveProvider,
        'stripe': StripeProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown payment provider: {provider_name}")
    
    return provider_class(secret_key)
