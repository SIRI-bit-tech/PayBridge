"""
Celery Tasks for Billing System
"""
from celery import shared_task
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .billing_models import PaymentAttempt, BillingSubscription, Payment
from .billing_subscription_service import BillingSubscriptionService
from .payment_providers import get_payment_provider
from .redis_pubsub import publish_event

logger = logging.getLogger(__name__)


@shared_task(name='billing.retry_failed_payment')
def retry_failed_payment(payment_attempt_id):
    """Retry a failed payment attempt"""
    try:
        attempt = PaymentAttempt.objects.get(id=payment_attempt_id)
        
        # Check if already succeeded
        if attempt.status == 'success':
            logger.info(f"Payment attempt {payment_attempt_id} already succeeded")
            return
        
        # Check if max retries reached
        if attempt.attempt_number >= 3:
            logger.warning(f"Max retries reached for payment attempt {payment_attempt_id}")
            attempt.status = 'failed'
            attempt.error_message = 'Max retry attempts reached'
            attempt.save()
            return
        
        # Get payment provider
        payment = attempt.payment
        if not payment:
            logger.error(f"No payment found for attempt {payment_attempt_id}")
            return
        
        provider = get_payment_provider(payment.provider)
        
        # First, check if payment was already processed
        verification = provider.verify_payment(payment.payment_intent)
        
        if verification['success']:
            # Payment was successful - confirm upgrade FIRST before marking as success
            try:
                # Upgrade subscription (this checks if payment is already "success" and short-circuits)
                result = BillingSubscriptionService.confirm_payment_and_upgrade(
                    payment.payment_intent,
                    payment.provider
                )
                
                if not result.get('success'):
                    logger.error(f"Subscription upgrade failed for payment {payment.payment_intent}: {result.get('error')}")
                    # Don't mark as success, retry later
                    raise Exception(result.get('error', 'Subscription upgrade failed'))
                
                # Only after successful upgrade, mark payment and attempt as successful
                attempt.status = 'success'
                attempt.provider_response = verification.get('raw_response', {})
                attempt.save()
                
                payment.status = 'success'
                payment.completed_at = timezone.now()
                payment.provider_response = verification.get('raw_response', {})
                payment.save()
                
                logger.info(f"Payment {payment.payment_intent} processed and subscription upgraded successfully")
                return
                
            except Exception as e:
                logger.error(f"Error upgrading subscription for payment {payment.payment_intent}: {str(e)}")
                
                # Check if max retries reached before retrying
                if attempt.attempt_number >= 3:
                    # Max retries reached - mark as failed
                    attempt.status = 'failed'
                    attempt.error_message = f'Subscription upgrade failed after max retries: {str(e)}'
                    attempt.provider_response = {'error': str(e), 'max_retries_reached': True}
                    attempt.save()
                    
                    # Also mark payment as failed
                    payment.status = 'failed'
                    payment.error_message = f'Subscription upgrade failed: {str(e)}'
                    payment.save()
                    
                    logger.error(f"Payment {payment.payment_intent} failed permanently after max retries")
                    return
                
                # Under retry limit - schedule retry
                raise self.retry(exc=e, countdown=3600)  # Retry in 1 hour
        
        # Safely extract status and error from verification
        status = verification.get('status')
        error = verification.get('error')
        
        # Derive concrete status if missing
        if status is None:
            if error:
                # Check for transient errors that should be retried
                transient_errors = ['timeout', 'network', 'connection', 'unavailable', 'rate limit']
                is_transient = any(keyword in str(error).lower() for keyword in transient_errors)
                status = 'pending' if is_transient else 'failed'
            else:
                status = 'failed'
        
        # If still pending or processing, schedule another retry
        if status in ['pending', 'processing']:
            attempt.attempt_number += 1
            attempt.retry_scheduled_for = timezone.now() + timedelta(hours=2)
            if error:
                attempt.error_message = str(error)
            attempt.save()
            
            # Schedule next retry
            retry_failed_payment.apply_async(
                args=[str(payment_attempt_id)],
                countdown=7200  # 2 hours
            )
            
            logger.info(f"Scheduled retry {attempt.attempt_number} for payment {payment.payment_intent}")
        else:
            # Payment failed permanently
            attempt.status = 'failed'
            attempt.error_message = error or 'Payment failed'
            attempt.save()
            
            payment.status = 'failed'
            payment.error_message = error or 'Payment failed'
            payment.save()
            
            logger.error(f"Payment {payment.payment_intent} failed permanently: {error}")
        
    except PaymentAttempt.DoesNotExist:
        logger.error(f"Payment attempt {payment_attempt_id} not found")
    except Exception as e:
        logger.error(f"Error retrying payment: {str(e)}")


@shared_task(name='billing.check_expired_subscriptions')
def check_expired_subscriptions():
    """Check for expired subscriptions and handle renewals/downgrades"""
    try:
        now = timezone.now()
        
        # Find subscriptions that need renewal
        expired_subscriptions = BillingSubscription.objects.filter(
            renewal_date__lte=now,
            status='active'
        )
        
        logger.info(f"Found {expired_subscriptions.count()} expired subscriptions")
        
        for subscription in expired_subscriptions:
            try:
                # If it's a paid plan, try to renew
                if subscription.plan.price > 0:
                    # Check if there's a recent successful payment
                    recent_payment = Payment.objects.filter(
                        user=subscription.user,
                        subscription=subscription,
                        status='success',
                        created_at__gte=now - timedelta(days=5)
                    ).first()
                    
                    if recent_payment:
                        # Extend renewal date
                        subscription.renewal_date = now + timedelta(days=subscription.plan.duration_days)
                        subscription.save()
                        
                        logger.info(f"Renewed subscription for {subscription.user.email}")
                        
                        # Emit event
                        publish_event('billing_updates', {
                            'type': 'plan:renewed',
                            'user_id': subscription.user.id,
                            'plan': subscription.plan.tier,
                            'renewal_date': subscription.renewal_date.isoformat(),
                        })
                    else:
                        # No recent payment, downgrade to free
                        free_plan = BillingSubscriptionService.get_or_create_free_plan()
                        subscription.plan = free_plan
                        subscription.status = 'active'
                        subscription.renewal_date = now + timedelta(days=30)
                        subscription.save()
                        
                        logger.info(f"Downgraded {subscription.user.email} to Free plan")
                        
                        # Emit event
                        publish_event('billing_updates', {
                            'type': 'plan:downgraded',
                            'user_id': subscription.user.id,
                            'plan': 'free',
                            'reason': 'payment_failed',
                        })
                else:
                    # Free plan, just extend renewal date
                    subscription.renewal_date = now + timedelta(days=30)
                    subscription.save()
                
            except Exception as e:
                logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
                continue
        
        logger.info("Finished checking expired subscriptions")
        
    except Exception as e:
        logger.error(f"Error in check_expired_subscriptions: {str(e)}")


@shared_task(name='billing.sync_usage_to_database')
def sync_usage_to_database():
    """Sync Redis usage data to database"""
    try:
        from .usage_tracking_service import UsageTrackingService
        
        # Get all active subscriptions
        subscriptions = BillingSubscription.objects.filter(status='active')
        
        logger.info(f"Syncing usage for {subscriptions.count()} subscriptions")
        
        for subscription in subscriptions:
            try:
                UsageTrackingService.sync_to_database(subscription.user)
            except Exception as e:
                logger.error(f"Error syncing usage for user {subscription.user.email}: {str(e)}")
                continue
        
        logger.info("Finished syncing usage to database")
        
    except Exception as e:
        logger.error(f"Error in sync_usage_to_database: {str(e)}")


@shared_task(name='billing.initialize_plans')
def initialize_plans():
    """Initialize default billing plans"""
    try:
        from .billing_models import Plan, Feature
        
        # Create plans
        plans_data = [
            {
                'name': 'Free',
                'tier': 'free',
                'price': 0,
                'currency': 'USD',
                'duration': 'monthly',
                'duration_days': 30,
                'api_limit': 100,
                'webhook_limit': 1,
                'has_analytics': False,
                'analytics_level': 'none',
            },
            {
                'name': 'Starter',
                'tier': 'starter',
                'price': 29,
                'currency': 'USD',
                'duration': 'monthly',
                'duration_days': 30,
                'api_limit': 10000,
                'webhook_limit': 1,
                'has_analytics': True,
                'analytics_level': 'basic',
            },
            {
                'name': 'Growth',
                'tier': 'growth',
                'price': 99,
                'currency': 'USD',
                'duration': 'monthly',
                'duration_days': 30,
                'api_limit': 100000,
                'webhook_limit': 5,
                'has_analytics': True,
                'analytics_level': 'advanced',
            },
            {
                'name': 'Enterprise',
                'tier': 'enterprise',
                'price': 0,  # Custom pricing
                'currency': 'USD',
                'duration': 'monthly',
                'duration_days': 30,
                'api_limit': 999999999,  # Unlimited
                'webhook_limit': 999,
                'has_analytics': True,
                'analytics_level': 'advanced',
                'has_priority_support': True,
                'has_custom_branding': True,
            },
        ]
        
        for plan_data in plans_data:
            plan, created = Plan.objects.update_or_create(
                tier=plan_data['tier'],
                defaults=plan_data
            )
            if created:
                logger.info(f"Created plan: {plan.name}")
            else:
                logger.info(f"Updated plan: {plan.name}")
        
        # Create features
        features_data = [
            {
                'code': 'basic_analytics',
                'name': 'Basic Analytics',
                'description': 'View basic transaction analytics',
                'plan_tier_access': ['starter', 'growth', 'enterprise'],
            },
            {
                'code': 'advanced_analytics',
                'name': 'Advanced Analytics',
                'description': 'Advanced analytics with custom reports',
                'plan_tier_access': ['growth', 'enterprise'],
            },
            {
                'code': 'priority_support',
                'name': 'Priority Support',
                'description': '24/7 priority customer support',
                'plan_tier_access': ['enterprise'],
            },
            {
                'code': 'custom_branding',
                'name': 'Custom Branding',
                'description': 'White-label and custom branding options',
                'plan_tier_access': ['enterprise'],
            },
            {
                'code': 'multiple_webhooks',
                'name': 'Multiple Webhooks',
                'description': 'Configure multiple webhook endpoints',
                'plan_tier_access': ['growth', 'enterprise'],
            },
        ]
        
        for feature_data in features_data:
            feature, created = Feature.objects.update_or_create(
                code=feature_data['code'],
                defaults=feature_data
            )
            if created:
                logger.info(f"Created feature: {feature.name}")
            else:
                logger.info(f"Updated feature: {feature.name}")
        
        logger.info("Plans and features initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing plans: {str(e)}")
