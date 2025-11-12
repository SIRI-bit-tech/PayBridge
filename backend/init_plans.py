"""
Quick script to initialize billing plans
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
django.setup()

from api.billing_models import Plan, Feature

print("Creating billing plans...")

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
        'price': 499,  # Custom pricing - Contact sales
        'currency': 'USD',
        'duration': 'monthly',
        'duration_days': 30,
        'api_limit': 999999999,
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
    print(f"{'✓ Created' if created else '→ Updated'} plan: {plan.name}")

print("\nCreating features...")

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
    print(f"{'✓ Created' if created else '→ Updated'} feature: {feature.name}")

print("\n✓ Done! Billing plans and features initialized.")
