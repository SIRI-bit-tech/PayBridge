# Generated migration for safe data migration
# This migration copies data from old Subscription/BillingPlan to new BillingSubscription/Plan models

from django.db import migrations, transaction


def migrate_billing_data(apps, schema_editor):
    """
    Safely migrate data from old billing models to new ones.
    This should be run BEFORE deleting the old models.
    """
    # Get old models (if they exist)
    try:
        Subscription = apps.get_model('api', 'Subscription')
        BillingPlan = apps.get_model('api', 'BillingPlan')
    except LookupError:
        # Models don't exist, nothing to migrate
        print("Old billing models not found - skipping data migration")
        return
    
    # Get new models
    BillingSubscription = apps.get_model('api', 'BillingSubscription')
    Plan = apps.get_model('api', 'Plan')
    Invoice = apps.get_model('api', 'Invoice')
    
    with transaction.atomic():
        # Step 1: Migrate BillingPlan to Plan
        old_plans = BillingPlan.objects.all()
        plan_mapping = {}  # Map old plan IDs to new plan IDs
        
        for old_plan in old_plans:
            # Check if plan already exists in new model
            new_plan, created = Plan.objects.get_or_create(
                name=old_plan.name,
                defaults={
                    'tier': getattr(old_plan, 'tier', 'free'),
                    'price': getattr(old_plan, 'price', 0),
                    'currency': getattr(old_plan, 'currency', 'USD'),
                    'duration': getattr(old_plan, 'duration', 'monthly'),
                    'duration_days': getattr(old_plan, 'duration_days', 30),
                    'api_limit': getattr(old_plan, 'api_limit', 100),
                    'webhook_limit': getattr(old_plan, 'webhook_limit', 1),
                    'has_analytics': getattr(old_plan, 'has_analytics', False),
                    'analytics_level': getattr(old_plan, 'analytics_level', 'none'),
                    'has_priority_support': getattr(old_plan, 'has_priority_support', False),
                    'has_custom_branding': getattr(old_plan, 'has_custom_branding', False),
                    'is_active': getattr(old_plan, 'is_active', True),
                }
            )
            plan_mapping[old_plan.id] = new_plan.id
            if created:
                print(f"Migrated plan: {old_plan.name}")
        
        # Step 2: Migrate Subscription to BillingSubscription
        old_subscriptions = Subscription.objects.all()
        subscription_mapping = {}  # Map old subscription IDs to new subscription IDs
        
        for old_sub in old_subscriptions:
            # Get the new plan ID
            old_plan_id = old_sub.plan_id
            new_plan_id = plan_mapping.get(old_plan_id)
            
            if not new_plan_id:
                print(f"Warning: Could not find new plan for subscription {old_sub.id}")
                continue
            
            new_plan = Plan.objects.get(id=new_plan_id)
            
            # Check if subscription already exists
            new_sub, created = BillingSubscription.objects.get_or_create(
                user=old_sub.user,
                defaults={
                    'plan': new_plan,
                    'status': getattr(old_sub, 'status', 'active'),
                    'start_date': getattr(old_sub, 'start_date', old_sub.created_at),
                    'renewal_date': getattr(old_sub, 'renewal_date', old_sub.created_at),
                    'auto_renew': getattr(old_sub, 'auto_renew', True),
                    'created_at': old_sub.created_at,
                    'updated_at': old_sub.updated_at,
                }
            )
            subscription_mapping[old_sub.id] = new_sub.id
            if created:
                print(f"Migrated subscription for user: {old_sub.user.email}")
        
        # Step 3: Update Invoice references (if Invoice has subscription field)
        try:
            invoices_with_old_sub = Invoice.objects.filter(subscription__isnull=False)
            for invoice in invoices_with_old_sub:
                old_sub_id = invoice.subscription_id
                new_sub_id = subscription_mapping.get(old_sub_id)
                
                if new_sub_id:
                    # Note: This assumes Invoice model has been updated to have billing_subscription field
                    # If not, this will need to be adjusted
                    if hasattr(invoice, 'billing_subscription_id'):
                        invoice.billing_subscription_id = new_sub_id
                        invoice.save(update_fields=['billing_subscription_id'])
                        print(f"Updated invoice {invoice.id} to new subscription")
        except Exception as e:
            print(f"Note: Could not update invoices: {e}")
        
        print(f"Migration complete: {len(plan_mapping)} plans, {len(subscription_mapping)} subscriptions")


def reverse_migration(apps, schema_editor):
    """
    Reverse is not safe - would require recreating old models.
    Use database backup to restore if needed.
    """
    print("WARNING: Reverse migration not implemented - restore from backup if needed")


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_billingsubscription_feature_payment_paymentattempt_and_more'),
    ]

    operations = [
        migrations.RunPython(
            migrate_billing_data,
            reverse_code=reverse_migration
        ),
    ]
