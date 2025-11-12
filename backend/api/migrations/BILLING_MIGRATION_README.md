# Billing Data Migration Guide

## ⚠️ CRITICAL: Data Migration Required

The billing system has been refactored from `Subscription`/`BillingPlan` to `BillingSubscription`/`Plan`.

## Migration Order

**IMPORTANT**: These migrations MUST be run in order:

1. **0007a_migrate_billing_data.py** - Copies data from old models to new models
2. **0007_delete_billingplan_remove_invoice_subscription_and_more.py** - Deletes old models

## Before Running Migrations

### 1. Backup Your Database
```bash
# PostgreSQL
pg_dump -U your_user -d paybridge > backup_before_billing_migration.sql

# Or use your database backup tool
```

### 2. Test on Development/Staging First
```bash
# Run migrations on a copy of production data
python manage.py migrate api 0007a_migrate_billing_data
python manage.py migrate api 0007
```

### 3. Verify Data Migration
```python
# In Django shell
python manage.py shell

from api.models import Plan, BillingSubscription

# Check that plans were migrated
print(f"Plans: {Plan.objects.count()}")
for plan in Plan.objects.all():
    print(f"  - {plan.name}: {plan.tier}")

# Check that subscriptions were migrated
print(f"Subscriptions: {BillingSubscription.objects.count()}")
for sub in BillingSubscription.objects.all():
    print(f"  - User: {sub.user.email}, Plan: {sub.plan.name}")
```

## Running Migrations in Production

### Step 1: Backup
```bash
# Create backup
pg_dump -U your_user -d paybridge > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Run Data Migration
```bash
# This copies data without deleting anything
python manage.py migrate api 0007a_migrate_billing_data
```

### Step 3: Verify Data
```bash
# Check that data was copied correctly
python manage.py shell
# Run verification queries (see above)
```

### Step 4: Run Deletion Migration
```bash
# Only after verifying data was copied!
python manage.py migrate api 0007
```

## Rollback Plan

If something goes wrong:

### Option 1: Restore from Backup
```bash
# PostgreSQL
psql -U your_user -d paybridge < backup_before_billing_migration.sql
```

### Option 2: Reverse Migrations (if data still exists)
```bash
# Reverse to before data migration
python manage.py migrate api 0006
```

## What Gets Migrated

### BillingPlan → Plan
- name
- tier
- price
- currency
- duration
- api_limit
- webhook_limit
- has_analytics
- analytics_level
- has_priority_support
- has_custom_branding

### Subscription → BillingSubscription
- user
- plan (mapped to new Plan)
- status
- start_date
- renewal_date
- auto_renew
- created_at
- updated_at

### Invoice Updates
- subscription → billing_subscription (if field exists)

## Troubleshooting

### Migration fails with "Model not found"
- The old models may have already been deleted
- Check if you have data in the old tables
- If no data exists, the migration will skip safely

### Data not appearing in new models
- Check migration output for errors
- Verify old models had data: `SELECT * FROM api_subscription;`
- Check logs for specific error messages

### Foreign key errors
- Ensure all related models are migrated first
- Check that user accounts still exist

## Support

If you encounter issues:
1. Check the migration output logs
2. Verify database backup exists
3. Test on a database copy first
4. Contact the development team before proceeding in production

## Post-Migration Cleanup

After verifying everything works:
1. Keep the backup for at least 30 days
2. Monitor for any billing-related errors
3. Verify all billing features work correctly
4. Check that subscriptions are being created properly
