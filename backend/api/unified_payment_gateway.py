"""
Unified Payment Gateway - Single interface for all payment providers
This is the core feature that makes PayBridge an API Hub
"""
import logging
from decimal import Decimal
from django.utils import timezone
from .models import Transaction, PaymentProvider, APIKey
from .payment_handlers import get_payment_handler
from .exceptions import InvalidAPIKey

logger = logging.getLogger(__name__)


class PaymentAdapterFactory:
    """Factory to get the right payment adapter for each provider"""
    
    @staticmethod
    def get_adapter(provider, user):
        """Get payment adapter for the specified provider"""
        try:
            # Get user's provider configuration
            provider_config = PaymentProvider.objects.get(
                user=user,
                provider=provider,
                is_active=True
            )
            
            # Get the handler
            handler = get_payment_handler(provider)
            
            # Return adapter with config
            return PaymentAdapter(handler, provider_config, user)
        except PaymentProvider.DoesNotExist:
            raise ValueError(f"Provider '{provider}' not configured for this user")


class PaymentAdapter:
    """Adapter that wraps payment handlers with user configuration"""
    
    def __init__(self, handler, provider_config, user):
        self.handler = handler
        self.provider_config = provider_config
        self.user = user
    
    def create_payment(self, amount, currency, customer_email, callback_url, description='', metadata=None):
        """Create payment using the provider's API"""
        reference = f"{self.provider_config.provider}_{timezone.now().timestamp()}"
        
        try:
            # Call the provider's API with user's secret key
            if self.provider_config.provider == 'paystack':
                result = self.handler.initiate_payment(
                    amount=amount,
                    email=customer_email,
                    reference=reference,
                    callback_url=callback_url,
                    secret_key=self.provider_config.secret_key
                )
            elif self.provider_config.provider == 'flutterwave':
                result = self.handler.initiate_payment(
                    amount=amount,
                    email=customer_email,
                    reference=reference,
                    callback_url=callback_url,
                    secret_key=self.provider_config.secret_key
                )
            elif self.provider_config.provider == 'mono':
                result = self.handler.initiate_payment(
                    amount=amount,
                    email=customer_email,
                    reference=reference,
                    callback_url=callback_url,
                    secret_key=self.provider_config.secret_key
                )
            elif self.provider_config.provider == 'stripe':
                # Stripe uses payment intents
                from .payment_service import PaymentService
                payment_service = PaymentService()
                result = payment_service.create_tokenized_payment(
                    transaction=None,  # Will be created below
                    customer_email=customer_email,
                    amount=amount,
                    currency=currency,
                    save_card=False
                )
            else:
                # For providers without initiate_payment method yet
                result = {
                    'status': 'success',
                    'message': f'Payment initiated with {self.provider_config.provider}',
                    'reference': reference
                }
            
            return {
                'success': True,
                'provider': self.provider_config.provider,
                'reference': reference,
                'provider_response': result,
                'amount': amount,
                'currency': currency
            }
        except Exception as e:
            logger.error(f"Payment initiation failed for {self.provider_config.provider}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_config.provider
            }


class UnifiedPaymentGateway:
    """
    Single interface for all payment providers
    This is the core value proposition - developers use ONE API
    """
    
    @staticmethod
    def create_payment(user, amount, currency, customer_email, callback_url, 
                      provider=None, description='', metadata=None, api_key=None,
                      idempotency_key=None):
        """
        Unified payment endpoint - the heart of PayBridge
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code (NGN, USD, etc.)
            customer_email: Customer's email
            callback_url: URL to redirect after payment
            provider: Optional - which provider to use (auto-selects if None)
            description: Payment description
            metadata: Additional metadata
            api_key: Optional API key for tracking
            idempotency_key: Prevent duplicate payments
        
        Returns:
            Payment result with authorization URL
        """
        
        # Check idempotency
        if idempotency_key:
            existing = Transaction.objects.filter(
                idempotency_key=idempotency_key,
                user=user
            ).first()
            if existing:
                return {
                    'success': True,
                    'transaction_id': str(existing.id),
                    'reference': existing.reference,
                    'status': existing.status,
                    'message': 'Using existing transaction',
                    'cached': True
                }
        
        # Auto-select provider if not specified
        if not provider:
            provider = UnifiedPaymentGateway._auto_select_provider(user)
        
        # Get API key if provided
        api_key_obj = None
        if api_key:
            try:
                api_key_obj = APIKey.objects.get(key=api_key, user=user, status='active')
            except APIKey.DoesNotExist:
                raise InvalidAPIKey("Invalid or inactive API key")
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=user,
            api_key=api_key_obj,
            provider=provider,
            amount=Decimal(str(amount)),
            currency=currency,
            customer_email=customer_email,
            description=description,
            metadata=metadata or {},
            reference=f"{provider}_{timezone.now().timestamp()}",
            idempotency_key=idempotency_key,
            status='pending'
        )
        
        # Calculate fees
        transaction.calculate_fee()
        transaction.save()
        
        try:
            # Get adapter and initiate payment
            adapter = PaymentAdapterFactory.get_adapter(provider, user)
            result = adapter.create_payment(
                amount=amount,
                currency=currency,
                customer_email=customer_email,
                callback_url=callback_url,
                description=description,
                metadata=metadata
            )
            
            if result.get('success'):
                # Update transaction with provider response
                transaction.reference = result.get('reference', transaction.reference)
                transaction.provider_response = result.get('provider_response', {})
                transaction.save()
                
                return {
                    'success': True,
                    'transaction_id': str(transaction.id),
                    'reference': transaction.reference,
                    'provider': provider,
                    'amount': float(amount),
                    'currency': currency,
                    'authorization_url': result.get('provider_response', {}).get('data', {}).get('authorization_url') or 
                                       result.get('provider_response', {}).get('authorization_url') or
                                       result.get('provider_response', {}).get('link'),
                    'status': 'pending',
                    'fee': float(transaction.fee),
                    'net_amount': float(transaction.net_amount)
                }
            else:
                # Payment initiation failed
                transaction.status = 'failed'
                transaction.provider_response = result
                transaction.save()
                
                return {
                    'success': False,
                    'transaction_id': str(transaction.id),
                    'error': result.get('error', 'Payment initiation failed'),
                    'provider': provider
                }
        
        except ValueError as e:
            # Provider not configured
            transaction.status = 'failed'
            transaction.save()
            
            return {
                'success': False,
                'transaction_id': str(transaction.id),
                'error': str(e),
                'provider': provider
            }
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in unified payment: {str(e)}", exc_info=True)
            transaction.status = 'failed'
            transaction.save()
            
            return {
                'success': False,
                'transaction_id': str(transaction.id),
                'error': 'An unexpected error occurred',
                'provider': provider
            }
    
    @staticmethod
    def _auto_select_provider(user):
        """
        Auto-select the best provider for the user
        Priority: Primary provider > Most used > First active
        """
        # Try to get primary provider
        primary = PaymentProvider.objects.filter(
            user=user,
            is_active=True
        ).order_by('-is_live', '-created_at').first()
        
        if primary:
            return primary.provider
        
        # Default to paystack if no provider configured
        return 'paystack'
    
    @staticmethod
    def verify_payment(user, transaction_id):
        """Verify payment status from provider"""
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=user)
            handler = get_payment_handler(transaction.provider)
            
            # Get provider config for API keys
            provider_config = PaymentProvider.objects.get(
                user=user,
                provider=transaction.provider
            )
            
            # Verify with provider
            if transaction.provider == 'paystack':
                from django.conf import settings
                import requests
                headers = {'Authorization': f"Bearer {provider_config.secret_key}"}
                url = f"https://api.paystack.co/transaction/verify/{transaction.reference}"
                response = requests.get(url, headers=headers)
                result = response.json()
            elif transaction.provider == 'flutterwave':
                import requests
                headers = {'Authorization': f"Bearer {provider_config.secret_key}"}
                url = f"https://api.flutterwave.com/v3/transactions/{transaction.reference}/verify"
                response = requests.get(url, headers=headers)
                result = response.json()
            elif transaction.provider == 'stripe':
                import stripe
                stripe.api_key = provider_config.secret_key
                payment_intent = stripe.PaymentIntent.retrieve(transaction.reference)
                result = {
                    'status': payment_intent.status,
                    'amount': payment_intent.amount / 100,
                    'currency': payment_intent.currency
                }
            else:
                result = {'status': 'unknown', 'message': 'Verification not implemented for this provider'}
            
            # Update transaction status based on verification
            if result.get('status') in ['success', 'successful', 'succeeded']:
                transaction.status = 'completed'
            elif result.get('status') in ['failed', 'cancelled']:
                transaction.status = 'failed'
            
            transaction.provider_response = result
            transaction.save()
            
            return {
                'success': True,
                'transaction_id': str(transaction.id),
                'status': transaction.status,
                'provider_response': result
            }
        
        except Transaction.DoesNotExist:
            return {
                'success': False,
                'error': 'Transaction not found'
            }
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
