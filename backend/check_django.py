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
        from django.core.cache import cache
        cache.set('test', 'ok', 30)
        print("✓ Redis connection working")
        
        # Check if we can import ASGI application
        from paybridge.asgi import application
        print("✓ ASGI application can be imported")
        
        # Check if we can import WSGI application  
        from paybridge.wsgi import application as wsgi_app
        print("✓ WSGI application can be imported")
        
        print("✓ All checks passed - Django should start successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()