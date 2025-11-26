#!/usr/bin/env python
"""
Debug environment variables
"""
import os

def debug_env():
    """Debug environment variables"""
    print("🔍 Environment Variable Debug:")
    
    redis_url = os.environ.get('REDIS_URL', 'NOT_SET')
    print(f"REDIS_URL raw: '{redis_url}'")
    print(f"REDIS_URL length: {len(redis_url)}")
    print(f"REDIS_URL starts with: '{redis_url[:20]}...'")
    
    if redis_url.startswith('='):
        print("❌ REDIS_URL has extra '=' at the beginning!")
        fixed_url = redis_url[1:]  # Remove the first character
        print(f"Fixed URL: '{fixed_url[:20]}...'")
        os.environ['REDIS_URL'] = fixed_url
        print("✅ Fixed REDIS_URL by removing extra '='")
    
    # Check other Redis vars
    celery_broker = os.environ.get('CELERY_BROKER_URL', 'NOT_SET')
    celery_result = os.environ.get('CELERY_RESULT_BACKEND', 'NOT_SET')
    
    print(f"CELERY_BROKER_URL: '{celery_broker[:30]}...'")
    print(f"CELERY_RESULT_BACKEND: '{celery_result[:30]}...'")

if __name__ == '__main__':
    debug_env()