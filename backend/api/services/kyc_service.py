import requests
import redis
import json
from django.conf import settings
from datetime import datetime, timedelta
from .models import KYCVerification
import logging

logger = logging.getLogger(__name__)
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


class KYCService:
    """Unified KYC verification service for BVN, NIN, and account verification"""
    
    @staticmethod
    def verify_bvn(user, bvn):
        """Verify Bank Verification Number via Mono"""
        cache_key = f"kyc:bvn:{bvn}"
        
        # Check cache first (24 hour TTL)
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            headers = {'Authorization': f'Bearer {settings.MONO_API_KEY}'}
            response = requests.post(
                'https://api.mono.co/api/v1/kyc/bvn/verify',
                json={'bvn': bvn},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                redis_client.setex(cache_key, 86400, json.dumps(data))
                
                # Create verification record
                verification = KYCVerification.objects.create(
                    user=user,
                    verification_type='bvn',
                    verification_id=bvn,
                    status='verified',
                    provider='mono',
                    provider_reference=data.get('id'),
                    verification_data=data,
                    verified_at=datetime.now()
                )
                
                return {'status': 'verified', 'data': data}
            else:
                return {'status': 'failed', 'error': response.text}
        except Exception as e:
            logger.error(f"BVN verification error: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    @staticmethod
    def verify_nin(user, nin):
        """Verify National Identification Number via Okra"""
        cache_key = f"kyc:nin:{nin}"
        
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            headers = {'Authorization': f'Bearer {settings.OKRA_API_KEY}'}
            response = requests.post(
                'https://api.okra.ng/api/v1/identity/nin/match',
                json={'nin': nin},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                redis_client.setex(cache_key, 86400, json.dumps(data))
                
                verification = KYCVerification.objects.create(
                    user=user,
                    verification_type='nin',
                    verification_id=nin,
                    status='verified',
                    provider='okra',
                    provider_reference=data.get('reference'),
                    verification_data=data,
                    verified_at=datetime.now()
                )
                
                return {'status': 'verified', 'data': data}
            else:
                return {'status': 'failed', 'error': response.text}
        except Exception as e:
            logger.error(f"NIN verification error: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    @staticmethod
    def verify_account(user, account_number, bank_code):
        """Verify bank account details via Mono"""
        cache_key = f"kyc:account:{bank_code}:{account_number}"
        
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            headers = {'Authorization': f'Bearer {settings.MONO_API_KEY}'}
            response = requests.post(
                'https://api.mono.co/api/v1/kyc/account/verify',
                json={
                    'account_number': account_number,
                    'bank_code': bank_code
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                redis_client.setex(cache_key, 86400, json.dumps(data))
                
                verification = KYCVerification.objects.create(
                    user=user,
                    verification_type='account',
                    verification_id=account_number,
                    status='verified',
                    provider='mono',
                    provider_reference=data.get('reference'),
                    verification_data=data,
                    verified_at=datetime.now()
                )
                
                return {'status': 'verified', 'data': data}
            else:
                return {'status': 'failed', 'error': response.text}
        except Exception as e:
            logger.error(f"Account verification error: {str(e)}")
            return {'status': 'error', 'error': str(e)}
