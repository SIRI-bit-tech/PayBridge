#!/usr/bin/env python
"""
Simple test script to verify Django can start
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
    django.setup()
    
    print("✓ Django setup successful")
    print("✓ Settings loaded")
    
    # Test database connection
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    
    # Test Redis connection
    try:
        from django.core.cache import cache
        cache.set('test', 'ok', 30)
        if cache.get('test') == 'ok':
            print("✓ Redis connection successful")
        else:
            print("✗ Redis connection failed")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
    
    print("Django test completed")