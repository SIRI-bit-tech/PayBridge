#!/usr/bin/env python
"""
Test Redis connection with SSL
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')
django.setup()

def test_redis_connection():
    """Test Redis connection with detailed error reporting"""
    print("🔍 Testing Redis Connection...")
    
    try:
        from django.core.cache import cache
        
        # Test basic connection
        print("📝 Testing cache set...")
        cache.set('test_key', 'test_value', 30)
        
        print("📖 Testing cache get...")
        result = cache.get('test_key')
        
        if result == 'test_value':
            print("✅ Redis connection successful!")
            print(f"   - Cache backend: {settings.CACHES['default']['BACKEND']}")
            print(f"   - Redis URL: {settings.CACHES['default']['LOCATION']}")
            return True
        else:
            print(f"⚠️  Redis connection partial - expected 'test_value', got '{result}'")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print(f"   - Error type: {type(e).__name__}")
        
        # Try to get more details about the connection
        try:
            import redis
            from urllib.parse import urlparse
            
            redis_url = settings.CACHES['default']['LOCATION']
            parsed = urlparse(redis_url)
            
            print(f"   - Host: {parsed.hostname}")
            print(f"   - Port: {parsed.port}")
            print(f"   - SSL: {'Yes' if parsed.scheme == 'rediss' else 'No'}")
            
        except Exception as detail_error:
            print(f"   - Could not get connection details: {detail_error}")
        
        return False

if __name__ == '__main__':
    success = test_redis_connection()
    exit(0 if success else 1)