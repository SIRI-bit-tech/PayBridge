import stripe
import logging
from django.conf import settings
from decimal import Decimal
from .models import Transaction

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for handling secure, tokenized payments"""
    
    def __init__(self):
        self.stripe_client = stripe
        self.stripe_client.api_key = settings.STRIPE_API_KEY
    
    def create_tokenized_payment(self, transaction, customer_email, amount, currency='usd', save_card=False):
        """
        Create a tokenized payment with Stripe.
        NEVER saves card details. Uses payment method tokens only.
        """
        try:
            logger.info(f"Creating tokenized payment for {customer_email}, amount: {amount}")
            
            # Create payment intent without storing payment method
            payment_intent = self.stripe_client.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                description=f"PayBridge Payment - {transaction.id}",
                metadata={
                    'transaction_id': str(transaction.id),
                    'customer_email': customer_email,
                    'idempotency_key': transaction.idempotency_key,
                },
                statement_descriptor='PAYBRIDGE',
                capture_method='automatic',  # Auto-capture on success
            )
            
            logger.info(f"Payment intent created: {payment_intent.id}")
            
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'payment_method_id': None,  # No payment method stored
                'requires_action': payment_intent.status == 'requires_action',
                'status': payment_intent.status,
            }
        except self.stripe_client.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            return {
                'success': False,
                'error': e.user_message,
                'error_code': e.code,
                'retry': True,
            }
        except self.stripe_client.error.RateLimitError as e:
            logger.error(f"Rate limit exceeded")
            return {
                'success': False,
                'error': 'Too many requests. Please try again later.',
                'retry': True,
                'retry_after': 60,
            }
        except self.stripe_client.error.InvalidRequestError as e:
            logger.error(f"Invalid request: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retry': False,
            }
        except self.stripe_client.error.AuthenticationError as e:
            logger.error(f"Authentication failed")
            return {
                'success': False,
                'error': 'Payment provider authentication failed',
                'retry': True,
            }
        except self.stripe_client.error.APIConnectionError as e:
            logger.error(f"Network error connecting to Stripe: {str(e)}")
            return {
                'success': False,
                'error': 'Network connection failed. Please check your internet and retry.',
                'retry': True,
                'retry_after': 5,
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred. Please try again.',
                'retry': True,
            }
    
    def confirm_payment_intent(self, payment_intent_id, payment_method_id=None):
        """Confirm a payment intent"""
        try:
            logger.info(f"Confirming payment intent: {payment_intent_id}")
            
            params = {'payment_method': payment_method_id} if payment_method_id else {}
            
            intent = self.stripe_client.PaymentIntent.confirm(
                payment_intent_id,
                **params
            )
            
            logger.info(f"Payment intent confirmed with status: {intent.status}")
            
            return {
                'success': intent.status in ['succeeded', 'processing'],
                'status': intent.status,
                'payment_intent': intent,
            }
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retry': True,
            }
    
    def handle_webhook_event(self, event, idempotency_key=None):
        """
        Handle Stripe webhook events.
        Idempotency ensures duplicate webhooks don't double-charge.
        """
        try:
            event_type = event['type']
            logger.info(f"Processing webhook event: {event_type}")
            
            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_succeeded(event['data']['object'], idempotency_key)
            elif event_type == 'payment_intent.payment_failed':
                return self._handle_payment_failed(event['data']['object'], idempotency_key)
            elif event_type == 'charge.failed':
                return self._handle_charge_failed(event['data']['object'], idempotency_key)
            
            logger.info(f"Unhandled event type: {event_type}")
            return {'handled': False}
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return {'error': str(e), 'handled': False}
    
    def _handle_payment_succeeded(self, payment_intent, idempotency_key=None):
        """Handle successful payment"""
        transaction_id = payment_intent.get('metadata', {}).get('transaction_id')
        
        if not transaction_id:
            logger.error("No transaction ID in payment metadata")
            return {'handled': False}
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            
            # Prevent double processing with idempotency check
            if transaction.status == 'completed':
                logger.info(f"Transaction {transaction_id} already completed")
                return {'handled': True, 'already_processed': True}
            
            transaction.status = 'completed'
            transaction.provider_response = {
                'payment_intent_id': payment_intent['id'],
                'charge_id': payment_intent.get('charges', {}).get('data', [{}])[0].get('id'),
            }
            transaction.save()
            
            logger.info(f"Transaction {transaction_id} marked as completed")
            return {'handled': True, 'transaction_id': transaction_id}
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found")
            return {'handled': False}
        except Exception as e:
            logger.error(f"Error processing succeeded payment: {str(e)}")
            return {'handled': False, 'error': str(e)}
    
    def _handle_payment_failed(self, payment_intent, idempotency_key=None):
        """Handle failed payment"""
        transaction_id = payment_intent.get('metadata', {}).get('transaction_id')
        
        if not transaction_id:
            logger.error("No transaction ID in payment metadata")
            return {'handled': False}
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.status = 'failed'
            transaction.provider_response = {
                'payment_intent_id': payment_intent['id'],
                'last_payment_error': payment_intent.get('last_payment_error'),
            }
            transaction.save()
            
            logger.info(f"Transaction {transaction_id} marked as failed")
            return {'handled': True, 'transaction_id': transaction_id}
        except Exception as e:
            logger.error(f"Error processing failed payment: {str(e)}")
            return {'handled': False}
    
    def _handle_charge_failed(self, charge, idempotency_key=None):
        """Handle failed charge"""
        # Extract transaction from charge metadata
        transaction_id = charge.get('metadata', {}).get('transaction_id')
        
        if not transaction_id:
            logger.error("No transaction ID in charge metadata")
            return {'handled': False}
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.status = 'failed'
            transaction.provider_response = {
                'charge_id': charge['id'],
                'failure_message': charge.get('failure_message'),
            }
            transaction.save()
            
            logger.info(f"Transaction {transaction_id} marked as failed due to charge failure")
            return {'handled': True}
        except Exception as e:
            logger.error(f"Error processing failed charge: {str(e)}")
            return {'handled': False}
