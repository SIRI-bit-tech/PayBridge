"""
Billing Subscription Service with Redis Pub/Sub
"""
import logging
import json
import uuid
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from .billing_models import Plan, BillingSubscription, Payment, PaymentAttempt, UsageTracking
from .payment_providers import get_payment_provider
from .redis_pubsub import publish_event
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis connection for usage tracking
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)


class BillingSubscriptionService:
    """Service for managing subscriptions and payments"""
    
    @staticmethod
    def get_or_create_free_plan():
        """Get or create the Free plan"""
        plan, created = Plan.objects.get_or_create(
            tier='free',
            defaults={
                'name': 'Free',
                'price': Decimal('0.00'),
                'currency': 'USD',
                'duration': 'monthly',
                'duration_days': 30,
                'api_limit': 100,
                'webhook_limit': 1,
                'has_analytics': False,
                'analytics_level': 'none',
            }
        )
        return plan
    
    @staticmethod
    def assign_free_plan_to_user(user):
        """Assign Free plan to new user"""
        try:
            # Check if user already has a subscription
            if hasattr(user, 'billing_subscription'):
                logger.info(f"User {user.email} already has a subscription")
                return user.billing_subscription
            
            free_plan = BillingSubscriptionService.get_or_create_free_plan()
            
            subscription = BillingSubscription.objects.create(
                user=user,
                plan=free_plan,
                status='active',
                start_date=timezone.now(),
                renewal_date=timezone.now() + timedelta(days=30)
            )
            
            # Create initial usage tracking
            BillingSubscriptionService.create_usage_tracking(subscription)
            
            # Emit event
            publish_event('billing_updates', {
                'type': 'plan:assigned',
                'user_id': user.id,
                'plan': free_plan.tier,
                'status': 'active'
            })
            
            logger.info(f"Assigned Free plan to user {user.email}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error assigning free plan to user {user.email}: {str(e)}")
            raise
    
    @staticmethod
    def create_usage_tracking(subscription):
        """Create usage tracking record for current period"""
        now = timezone.now()
        period_end = subscription.renewal_date
        
        usage, created = UsageTracking.objects.get_or_create(
            user=subscription.user,
            subscription=subscription,
            period_start=subscription.start_date,
            period_end=period_end,
            defaults={
                'api_calls_used': 0,
                'webhooks_used': 0,
                'analytics_requests': 0,
            }
        )
        
        # Also store in Redis for fast access
        redis_key = f"usage:{subscription.user.id}:{now.strftime('%Y-%m')}"
        if created:
            redis_client.hset(redis_key, mapping={
                'api_calls': 0,
                'webhooks': 0,
                'analytics': 0,
            })
            redis_client.expire(redis_key, 60 * 60 * 24 * 35)  # 35 days
        
        return usage
    
    @staticmethod
    def create_payment_session(user, plan_id, provider):
        """Create a payment session for subscription upgrade"""
        try:
            plan = Plan.objects.get(id=plan_id)
            
            if plan.price == 0:
                return {
                    'success': False,
                    'error': 'Cannot create payment session for free plan'
                }
            
            # Generate idempotency key
            idempotency_key = f"sub_{user.id}_{plan.id}_{uuid.uuid4().hex[:12]}"
            
            # Check for duplicate idempotency key
            existing_payment = Payment.objects.filter(idempotency_key=idempotency_key).first()
            if existing_payment:
                logger.info(f"Duplicate payment request detected: {idempotency_key}")
                return {
                    'success': True,
                    'payment_intent': existing_payment.payment_intent,
                    'transaction_id': existing_payment.transaction_id,
                    'status': existing_payment.status,
                    'duplicate': True
                }
            
            # Create payment intent with provider
            payment_provider = get_payment_provider(provider)
            
            result = payment_provider.create_payment_intent(
                amount=plan.price,
                currency=plan.currency,
                email=user.email,
                metadata={
                    'user_id': str(user.id),
                    'plan_id': str(plan.id),
                    'plan_name': plan.name,
                }
            )
            
            if not result['success']:
                return result
            
            # Create payment record
            payment = Payment.objects.create(
                user=user,
                provider=provider,
                transaction_id=result.get('reference', result['payment_intent']),
                payment_intent=result['payment_intent'],
                idempotency_key=idempotency_key,
                amount=plan.price,
                currency=plan.currency,
                status='pending',
                provider_response=result
            )
            
            logger.info(f"Payment session created for user {user.email}, plan {plan.name}")
            
            return {
                'success': True,
                'payment_id': str(payment.id),
                'payment_intent': payment.payment_intent,
                'transaction_id': payment.transaction_id,
                'idempotency_key': idempotency_key,
                'authorization_url': result.get('authorization_url'),
                'client_secret': result.get('client_secret'),
                'amount': float(plan.price),
                'currency': plan.currency,
                'plan': {
                    'id': str(plan.id),
                    'name': plan.name,
                    'tier': plan.tier,
                }
            }
            
        except Plan.DoesNotExist:
            return {
                'success': False,
                'error': 'Plan not found'
            }
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    @transaction.atomic
    def confirm_payment_and_upgrade(payment_intent, provider):
        """Confirm payment and upgrade user subscription"""
        try:
            # Find payment record
            payment = Payment.objects.select_for_update().get(payment_intent=payment_intent)
            
            # Check if already processed
            if payment.status == 'success':
                logger.info(f"Payment {payment_intent} already processed")
                return {
                    'success': True,
                    'message': 'Payment already processed',
                    'duplicate': True
                }
            
            # Verify payment with provider
            payment_provider = get_payment_provider(provider)
            verification = payment_provider.verify_payment(payment_intent)
            
            if not verification['success']:
                payment.status = 'failed'
                payment.error_message = verification.get('error', 'Payment verification failed')
                payment.save()
                
                return {
                    'success': False,
                    'error': verification.get('error', 'Payment verification failed')
                }
            
            # Update payment status
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.provider_response = verification.get('raw_response', {})
            payment.save()
            
            # Get plan from payment metadata
            plan_id = payment.provider_response.get('metadata', {}).get('plan_id')
            if not plan_id:
                # Try to get from payment record
                plan_id = payment.subscription.plan_id if payment.subscription else None
            
            if not plan_id:
                logger.error(f"No plan_id found for payment {payment_intent}")
                return {
                    'success': False,
                    'error': 'Plan information missing'
                }
            
            plan = Plan.objects.get(id=plan_id)
            user = payment.user
            
            # Update or create subscription
            subscription, created = BillingSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'status': 'active',
                    'start_date': timezone.now(),
                    'renewal_date': timezone.now() + timedelta(days=plan.duration_days),
                }
            )
            
            # Link payment to subscription
            payment.subscription = subscription
            payment.save()
            
            # Create new usage tracking for the period
            BillingSubscriptionService.create_usage_tracking(subscription)
            
            # Emit real-time event via Redis pub/sub
            event_data = {
                'type': 'plan:update',
                'user_id': user.id,
                'plan': {
                    'id': str(plan.id),
                    'name': plan.name,
                    'tier': plan.tier,
                    'api_limit': plan.api_limit,
                    'webhook_limit': plan.webhook_limit,
                    'has_analytics': plan.has_analytics,
                    'analytics_level': plan.analytics_level,
                },
                'status': 'active',
                'renewal_date': subscription.renewal_date.isoformat(),
            }
            
            publish_event('billing_updates', event_data)
            
            logger.info(f"User {user.email} upgraded to {plan.name}")
            
            return {
                'success': True,
                'subscription': {
                    'id': str(subscription.id),
                    'plan': plan.tier,
                    'status': subscription.status,
                    'renewal_date': subscription.renewal_date.isoformat(),
                },
                'payment': {
                    'id': str(payment.id),
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                }
            }
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {payment_intent}")
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def cancel_subscription(user):
        """Cancel user subscription"""
        try:
            subscription = user.billing_subscription
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            # Emit event
            publish_event('billing_updates', {
                'type': 'plan:cancelled',
                'user_id': user.id,
                'plan': subscription.plan.tier,
                'cancelled_at': subscription.cancelled_at.isoformat(),
            })
            
            logger.info(f"Subscription cancelled for user {user.email}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_subscription_info(user):
        """Get user subscription and usage info"""
        try:
            subscription = user.billing_subscription
            plan = subscription.plan
            
            # Get current usage
            now = timezone.now()
            usage = UsageTracking.objects.filter(
                user=user,
                period_start__lte=now,
                period_end__gte=now
            ).first()
            
            if not usage:
                usage = BillingSubscriptionService.create_usage_tracking(subscription)
            
            return {
                'subscription': {
                    'id': str(subscription.id),
                    'plan': {
                        'id': str(plan.id),
                        'name': plan.name,
                        'tier': plan.tier,
                        'price': float(plan.price),
                        'currency': plan.currency,
                        'api_limit': plan.api_limit,
                        'webhook_limit': plan.webhook_limit,
                        'has_analytics': plan.has_analytics,
                        'analytics_level': plan.analytics_level,
                    },
                    'status': subscription.status,
                    'start_date': subscription.start_date.isoformat(),
                    'renewal_date': subscription.renewal_date.isoformat(),
                    'days_until_renewal': subscription.days_until_renewal(),
                },
                'usage': {
                    'api_calls_used': usage.api_calls_used,
                    'api_calls_remaining': usage.get_api_calls_remaining(),
                    'api_calls_limit': plan.api_limit,
                    'webhooks_used': usage.webhooks_used,
                    'webhooks_limit': plan.webhook_limit,
                    'analytics_requests': usage.analytics_requests,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription info: {str(e)}")
            return None
