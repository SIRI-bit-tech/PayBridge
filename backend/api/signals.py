from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, AuditLog
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile and billing subscription on user creation"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        
        # Assign free billing plan (new billing system)
        try:
            from .billing_subscription_service import BillingSubscriptionService
            BillingSubscriptionService.assign_free_plan_to_user(instance)
            logger.info(f"Assigned free billing plan to user {instance.email}")
        except Exception as e:
            # Log full traceback for debugging
            logger.exception(f"Failed to assign free plan to user {instance.email}: {str(e)}")
            # Re-raise to surface the error to callers/monitoring
            raise


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
