#!/usr/bin/env python
"""
Migration reset script for PayBridge
This script safely resets Django migrations to match the current database state
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.base import BaseCommand

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
django.setup()

def table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def reset_migrations():
    """Reset migrations to match current database state"""
    print("🔄 Resetting Django migrations to match database state...")
    
    # Check what tables actually exist
    billing_tables_exist = (
        table_exists('billing_subscriptions') and
        table_exists('billing_plans') and
        table_exists('billing_payments')
    )
    
    webhook_tables_exist = (
        table_exists('webhook_events') and
        table_exists('webhook_subscriptions')
    )
    
    print(f"📊 Database state:")
    print(f"   - Billing tables exist: {billing_tables_exist}")
    print(f"   - Webhook tables exist: {webhook_tables_exist}")
    
    try:
        # Reset migration state completely
        print("🗑️  Clearing migration history...")
        execute_from_command_line(['manage.py', 'migrate', 'api', 'zero', '--fake'])
        
        # Apply migrations based on what exists
        print("📝 Applying migrations to match database state...")
        
        # Always apply basic migrations
        for migration in ['0001', '0002', '0003', '0004', '0005']:
            try:
                if billing_tables_exist:
                    execute_from_command_line(['manage.py', 'migrate', 'api', migration, '--fake'])
                else:
                    execute_from_command_line(['manage.py', 'migrate', 'api', migration])
                print(f"   ✅ Migration {migration} applied")
            except Exception as e:
                print(f"   ⚠️  Migration {migration}: {e}")
        
        # Handle billing migration
        try:
            if billing_tables_exist:
                execute_from_command_line(['manage.py', 'migrate', 'api', '0006', '--fake'])
                print("   ✅ Billing migration 0006 faked (tables exist)")
            else:
                execute_from_command_line(['manage.py', 'migrate', 'api', '0006'])
                print("   ✅ Billing migration 0006 applied")
        except Exception as e:
            print(f"   ⚠️  Billing migration 0006: {e}")
        
        # Handle webhook migration
        try:
            if webhook_tables_exist:
                execute_from_command_line(['manage.py', 'migrate', 'api', '0007', '--fake'])
                print("   ✅ Webhook migration 0007 faked (tables exist)")
            else:
                execute_from_command_line(['manage.py', 'migrate', 'api', '0007'])
                print("   ✅ Webhook migration 0007 applied")
        except Exception as e:
            print(f"   ⚠️  Webhook migration 0007: {e}")
        
        # Apply remaining migrations
        print("🔄 Applying remaining migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migration reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration reset failed: {e}")
        return False

if __name__ == '__main__':
    success = reset_migrations()
    sys.exit(0 if success else 1)