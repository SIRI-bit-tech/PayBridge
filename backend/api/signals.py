from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Subscription, AuditLog
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile and subscription on user creation"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        Subscription.objects.get_or_create(
            user=instance,
            defaults={
                'plan': 'starter',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
                'renewal_date': timezone.now() + timedelta(days=30),
            }
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile"""
    instance.profile.save()
