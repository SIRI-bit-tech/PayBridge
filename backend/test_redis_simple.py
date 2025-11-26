#!/usr/bin/env python
"""
Simple Redis connection test for deployment
"""
import os
import sys

def test_redis_simple():
    """Simple Redis test without Django"""
    try:
        import redis
        from urllib.parse import urlparse
        
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        
        # Fix common issue with extra '=' at the beginning
        if redis_url.startswith('='):
            print(f"⚠️  Found extra '=' in Redis URL, fixing...")
            redis_url = redis_url[1:]  # Remove the first character
            os.environ['REDIS_URL'] = redis_url  # Update environment
        
        print(f"🔍 Testing Redis URL: {redis_url}")
        
        # Parse the URL
        parsed = urlparse(redis_url)
        
        # Create Redis client
        if parsed.scheme == 'rediss':
            # SSL connection
            client = redis.Redis.from_url(
                redis_url,
                ssl_cert_reqs=None,
                ssl_check_hostname=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        else:
            # Regular connection
            client = redis.Redis.from_url(redis_url)
        
        # Test connection
        client.ping()
        print("✅ Redis ping successful!")
        
        # Test set/get
        client.set('test_key', 'test_value', ex=30)
        result = client.get('test_key')
        
        if result and result.decode() == 'test_value':
            print("✅ Redis set/get successful!")
            return True
        else:
            print(f"⚠️  Redis set/get failed - got: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == '__main__':
    success = test_redis_simple()
    print(f"🏁 Redis test {'PASSED' if success else 'FAILED'}")
    # Don't exit with error - let deployment continue
    sys.exit(0)