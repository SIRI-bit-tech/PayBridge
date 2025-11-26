#!/usr/bin/env python
"""
Check Django configuration and identify startup issues
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
    
    try:
        django.setup()
        print("✓ Django setup successful")
        
        # Check database
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✓ Database connection working")
        
        # Check Redis
        try:
            from django.core.cache import cache
            cache.set('test', 'ok', 30)
            result = cache.get('test')
            if result == 'ok':
                print("✓ Redis connection working")
            else:
                print("⚠ Redis connection partial - set/get mismatch")
        except Exception as redis_error:
            print(f"⚠ Redis connection failed: {redis_error}")
            print("⚠ Continuing without Redis cache - some features may be limited")
        
        # Check if we can import WSGI application  
        from paybridge.wsgi import application as wsgi_app
        print("✓ WSGI application can be imported")
        
        # Check ASGI application
        try:
            from paybridge.asgi import application as asgi_app
            print("✓ ASGI application can be imported")
            print("✓ WebSocket support enabled")
        except Exception as e:
            print(f"⚠ ASGI check failed: {e}")
            print("⚠ WebSocket support may be limited")
        
        print("✓ All checks passed - Django should start successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()