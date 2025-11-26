#!/usr/bin/env python
"""
Test script to validate migration fixes
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
django.setup()

def test_database_connection():
    """Test if we can connect to the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_migration_state():
    """Test current migration state"""
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        print(f"📊 Migration Status:")
        print(f"   - Pending migrations: {len(plan)}")
        
        if plan:
            print("   - Pending:")
            for migration, backwards in plan:
                direction = "REVERSE" if backwards else "APPLY"
                print(f"     • {migration} ({direction})")
        else:
            print("   - All migrations are up to date!")
            
        return len(plan) == 0
        
    except Exception as e:
        print(f"Migration state check failed: {e}")
        return False

def main():
    print("🧪 Testing PayBridge Migration Setup...")
    
    # Test database connection
    print("\n1️⃣ Testing database connection...")
    if test_database_connection():
        print("   ✅ Database connection successful")
    else:
        print("   ❌ Database connection failed")
        return False
    
    # Test migration state
    print("\n2️⃣ Checking migration state...")
    if test_migration_state():
        print("   ✅ All migrations are up to date")
    else:
        print("   ⚠️  Some migrations are pending")
    
    print("\n🏁 Migration test completed!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)