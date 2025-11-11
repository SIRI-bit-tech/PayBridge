"""
Real-time Usage Tracking Service with Redis
"""
import logging
import redis
from django.conf import settings
from django.utils import timezone
from .billing_models import UsageTracking
from .redis_pubsub import publish_event

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)


class UsageTrackingService:
    """Service for tracking real-time usage"""
    
    @staticmethod
    def get_redis_key(user_id, period=None):
        """Get Redis key for user usage"""
        if not period:
            period = timezone.now().strftime('%Y-%m')
        return f"usage:{user_id}:{period}"
    
    @staticmethod
    def increment_api_call(user):
        """Increment API call counter"""
        try:
            now = timezone.now()
            period = now.strftime('%Y-%m')
            redis_key = UsageTrackingService.get_redis_key(user.id, period)
            
            # Increment in Redis
            new_count = redis_client.hincrby(redis_key, 'api_calls', 1)
            redis_client.expire(redis_key, 60 * 60 * 24 * 35)  # 35 days
            
            # Get user's plan limit
            subscription = user.billing_subscription
            api_limit = subscription.plan.api_limit
            
            # Check if limit reached
            if new_count >= api_limit:
                # Emit limit reached event
                publish_event('billing_usage', {
                    'type': 'plan:limit_reached',
                    'user_id': user.id,
                    'resource': 'api_calls',
                    'used': new_count,
                    'limit': api_limit,
                })
                
                logger.warning(f"User {user.email} reached API limit: {new_count}/{api_limit}")
            
            # Emit usage update every 10 calls
            if new_count % 10 == 0:
                publish_event('billing_usage', {
                    'type': 'usage:update',
                    'user_id': user.id,
                    'api_calls_used': new_count,
                    'api_calls_remaining': max(0, api_limit - new_count),
                    'api_calls_limit': api_limit,
                })
            
            # Sync to database every 100 calls
            if new_count % 100 == 0:
                UsageTrackingService.sync_to_database(user)
            
            return new_count
            
        except Exception as e:
            logger.error(f"Error incrementing API call: {str(e)}")
            return 0
    
    @staticmethod
    def increment_webhook(user):
        """Increment webhook counter"""
        try:
            now = timezone.now()
            period = now.strftime('%Y-%m')
            redis_key = UsageTrackingService.get_redis_key(user.id, period)
            
            # Increment in Redis
            new_count = redis_client.hincrby(redis_key, 'webhooks', 1)
            redis_client.expire(redis_key, 60 * 60 * 24 * 35)
            
            # Get user's plan limit
            subscription = user.billing_subscription
            webhook_limit = subscription.plan.webhook_limit
            
            # Check if limit reached
            if new_count >= webhook_limit:
                publish_event('billing_usage', {
                    'type': 'plan:limit_reached',
                    'user_id': user.id,
                    'resource': 'webhooks',
                    'used': new_count,
                    'limit': webhook_limit,
                })
                
                logger.warning(f"User {user.email} reached webhook limit: {new_count}/{webhook_limit}")
            
            # Emit usage update
            publish_event('billing_usage', {
                'type': 'usage:update',
                'user_id': user.id,
                'webhooks_used': new_count,
                'webhooks_limit': webhook_limit,
            })
            
            return new_count
            
        except Exception as e:
            logger.error(f"Error incrementing webhook: {str(e)}")
            return 0
    
    @staticmethod
    def increment_analytics_request(user):
        """Increment analytics request counter"""
        try:
            now = timezone.now()
            period = now.strftime('%Y-%m')
            redis_key = UsageTrackingService.get_redis_key(user.id, period)
            
            # Increment in Redis
            new_count = redis_client.hincrby(redis_key, 'analytics', 1)
            redis_client.expire(redis_key, 60 * 60 * 24 * 35)
            
            # Emit usage update
            publish_event('billing_usage', {
                'type': 'usage:update',
                'user_id': user.id,
                'analytics_requests': new_count,
            })
            
            return new_count
            
        except Exception as e:
            logger.error(f"Error incrementing analytics request: {str(e)}")
            return 0
    
    @staticmethod
    def get_current_usage(user):
        """Get current usage from Redis"""
        try:
            now = timezone.now()
            period = now.strftime('%Y-%m')
            redis_key = UsageTrackingService.get_redis_key(user.id, period)
            
            usage_data = redis_client.hgetall(redis_key)
            
            if not usage_data:
                # Initialize if not exists
                redis_client.hset(redis_key, mapping={
                    'api_calls': 0,
                    'webhooks': 0,
                    'analytics': 0,
                })
                redis_client.expire(redis_key, 60 * 60 * 24 * 35)
                usage_data = {'api_calls': '0', 'webhooks': '0', 'analytics': '0'}
            
            subscription = user.billing_subscription
            plan = subscription.plan
            
            api_calls_used = int(usage_data.get('api_calls', 0))
            webhooks_used = int(usage_data.get('webhooks', 0))
            analytics_used = int(usage_data.get('analytics', 0))
            
            return {
                'api_calls_used': api_calls_used,
                'api_calls_remaining': max(0, plan.api_limit - api_calls_used),
                'api_calls_limit': plan.api_limit,
                'webhooks_used': webhooks_used,
                'webhooks_limit': plan.webhook_limit,
                'analytics_requests': analytics_used,
                'period': period,
            }
            
        except Exception as e:
            logger.error(f"Error getting current usage: {str(e)}")
            return None
    
    @staticmethod
    def check_api_limit(user):
        """Check if user has reached API limit"""
        try:
            usage = UsageTrackingService.get_current_usage(user)
            if not usage:
                return False
            
            return usage['api_calls_used'] >= usage['api_calls_limit']
            
        except Exception as e:
            logger.error(f"Error checking API limit: {str(e)}")
            return False
    
    @staticmethod
    def check_webhook_limit(user):
        """Check if user has reached webhook limit"""
        try:
            usage = UsageTrackingService.get_current_usage(user)
            if not usage:
                return False
            
            return usage['webhooks_used'] >= usage['webhooks_limit']
            
        except Exception as e:
            logger.error(f"Error checking webhook limit: {str(e)}")
            return False
    
    @staticmethod
    def check_feature_access(user, feature_code):
        """Check if user has access to a feature"""
        try:
            from .billing_models import Feature
            
            subscription = user.billing_subscription
            plan_tier = subscription.plan.tier
            
            feature = Feature.objects.filter(code=feature_code).first()
            if not feature:
                return True  # Feature doesn't exist, allow access
            
            return feature.is_available_for_plan(plan_tier)
            
        except Exception as e:
            logger.error(f"Error checking feature access: {str(e)}")
            return False
    
    @staticmethod
    def sync_to_database(user):
        """Sync Redis usage to database"""
        try:
            now = timezone.now()
            period = now.strftime('%Y-%m')
            redis_key = UsageTrackingService.get_redis_key(user.id, period)
            
            usage_data = redis_client.hgetall(redis_key)
            if not usage_data:
                return
            
            subscription = user.billing_subscription
            
            # Find or create usage tracking record
            usage_record = UsageTracking.objects.filter(
                user=user,
                period_start__lte=now,
                period_end__gte=now
            ).first()
            
            if usage_record:
                usage_record.api_calls_used = int(usage_data.get('api_calls', 0))
                usage_record.webhooks_used = int(usage_data.get('webhooks', 0))
                usage_record.analytics_requests = int(usage_data.get('analytics', 0))
                usage_record.save()
                
                logger.info(f"Synced usage to database for user {user.email}")
            
        except Exception as e:
            logger.error(f"Error syncing usage to database: {str(e)}")
