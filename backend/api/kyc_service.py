import requests
import logging
from django.utils import timezone
from .models import KYCVerification
from .exceptions import KYCVerificationFailed
from django.conf import settings

logger = logging.getLogger(__name__)


class MonoKYCProvider:
    """Mono API KYC provider"""
    BASE_URL = 'https://api.withmono.com/v1'
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def verify_bvn(self, bvn):
        """Verify Bank Verification Number"""
        url = f'{self.BASE_URL}/kyc/bvn/verify'
        payload = {'bvn': bvn}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Mono BVN verification error: {str(e)}")
            raise KYCVerificationFailed(f"BVN verification failed: {str(e)}")
    
    def verify_nin(self, nin):
        """Verify National Identification Number"""
        url = f'{self.BASE_URL}/kyc/nin/verify'
        payload = {'nin': nin}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Mono NIN verification error: {str(e)}")
            raise KYCVerificationFailed(f"NIN verification failed: {str(e)}")
    
    def verify_account(self, account_number, bank_code):
        """Verify account details"""
        url = f'{self.BASE_URL}/kyc/account/verify'
        payload = {'accountNumber': account_number, 'bankCode': bank_code}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Mono account verification error: {str(e)}")
            raise KYCVerificationFailed(f"Account verification failed: {str(e)}")


class OkraKYCProvider:
    """Okra API KYC provider"""
    BASE_URL = 'https://api.okra.ng/v1'
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def verify_bvn(self, bvn):
        """Verify Bank Verification Number"""
        url = f'{self.BASE_URL}/identities/bvn/match'
        payload = {'bvn': bvn}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Okra BVN verification error: {str(e)}")
            raise KYCVerificationFailed(f"BVN verification failed: {str(e)}")
    
    def verify_account(self, account_number, bank_code):
        """Verify account details"""
        url = f'{self.BASE_URL}/accounts/verify'
        payload = {'accountNumber': account_number, 'bankCode': bank_code}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Okra account verification error: {str(e)}")
            raise KYCVerificationFailed(f"Account verification failed: {str(e)}")


class KYCService:
    """Unified KYC verification service"""
    
    @staticmethod
    def verify_bvn(user, bvn, provider='mono'):
        """Verify BVN with caching"""
        # Check cache first (Redis would be ideal)
        existing = KYCVerification.objects.filter(
            user=user,
            verification_type='bvn',
            status='verified'
        ).first()
        
        if existing:
            return {'cached': True, 'data': existing.verification_data}
        
        # Initialize provider
        if provider == 'mono':
            provider_obj = MonoKYCProvider(settings.MONO_API_KEY)
        elif provider == 'okra':
            provider_obj = OkraKYCProvider(settings.OKRA_API_KEY)
        else:
            raise KYCVerificationFailed('Invalid KYC provider')
        
        # Verify with provider
        result = provider_obj.verify_bvn(bvn)
        
        # Create verification record
        kyc = KYCVerification.objects.create(
            user=user,
            verification_type='bvn',
            verification_id=bvn,
            provider=provider,
            provider_reference=result.get('id', ''),
            verification_data=result,
            status='verified' if result.get('isSuccessful') else 'failed'
        )
        
        if kyc.status == 'verified':
            kyc.verified_at = timezone.now()
            kyc.save()
        
        return {'cached': False, 'data': result}
    
    @staticmethod
    def verify_account(user, account_number, bank_code, provider='mono'):
        """Verify account number"""
        existing = KYCVerification.objects.filter(
            user=user,
            verification_type='account',
            status='verified'
        ).first()
        
        if existing:
            return {'cached': True, 'data': existing.verification_data}
        
        if provider == 'mono':
            provider_obj = MonoKYCProvider(settings.MONO_API_KEY)
        elif provider == 'okra':
            provider_obj = OkraKYCProvider(settings.OKRA_API_KEY)
        else:
            raise KYCVerificationFailed('Invalid KYC provider')
        
        result = provider_obj.verify_account(account_number, bank_code)
        
        kyc = KYCVerification.objects.create(
            user=user,
            verification_type='account',
            verification_id=account_number,
            provider=provider,
            provider_reference=result.get('id', ''),
            verification_data=result,
            status='verified' if result.get('isSuccessful') else 'failed'
        )
        
        if kyc.status == 'verified':
            kyc.verified_at = timezone.now()
            kyc.save()
        
        return {'cached': False, 'data': result}
