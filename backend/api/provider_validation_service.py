"""
Payment Provider Validation Service
Validates provider credentials by making test API calls
"""
import requests
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ProviderValidationService:
    """Service to validate payment provider credentials"""
    
    @staticmethod
    def validate_paystack(public_key: str, secret_key: str, mode: str) -> Tuple[bool, str]:
        """
        Validate Paystack credentials
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use the secret key to verify
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }
            
            # Make a simple API call to verify credentials
            response = requests.get(
                'https://api.paystack.co/bank',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, ""
            elif response.status_code == 401:
                return False, "Invalid Paystack credentials"
            else:
                return False, f"Paystack API error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Paystack API timeout"
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack validation error: {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    @staticmethod
    def validate_flutterwave(public_key: str, secret_key: str, mode: str) -> Tuple[bool, str]:
        """
        Validate Flutterwave credentials
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }
            
            # Make a simple API call to verify credentials
            response = requests.get(
                'https://api.flutterwave.com/v3/balances',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, ""
            elif response.status_code == 401:
                return False, "Invalid Flutterwave credentials"
            else:
                return False, f"Flutterwave API error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Flutterwave API timeout"
        except requests.exceptions.RequestException as e:
            logger.error(f"Flutterwave validation error: {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    @staticmethod
    def validate_stripe(public_key: str, secret_key: str, mode: str) -> Tuple[bool, str]:
        """
        Validate Stripe credentials
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import stripe as stripe_lib
            
            # Set the API key
            stripe_lib.api_key = secret_key
            
            # Make a simple API call to verify credentials
            # Retrieve account information
            account = stripe_lib.Account.retrieve()
            
            if account and account.id:
                return True, ""
            else:
                return False, "Invalid Stripe credentials"
                
        except stripe_lib.error.AuthenticationError:
            return False, "Invalid Stripe credentials"
        except stripe_lib.error.StripeError as e:
            logger.error(f"Stripe validation error: {str(e)}")
            return False, f"Stripe API error: {str(e)}"
        except Exception as e:
            logger.error(f"Stripe validation error: {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    @classmethod
    def validate_provider(cls, provider: str, public_key: str, secret_key: str, mode: str) -> Tuple[bool, str]:
        """
        Validate provider credentials based on provider type
        
        Args:
            provider: Provider name (paystack, flutterwave, stripe)
            public_key: Provider public key
            secret_key: Provider secret key
            mode: test or live
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if provider == 'paystack':
            return cls.validate_paystack(public_key, secret_key, mode)
        elif provider == 'flutterwave':
            return cls.validate_flutterwave(public_key, secret_key, mode)
        elif provider == 'stripe':
            return cls.validate_stripe(public_key, secret_key, mode)
        else:
            return False, f"Unknown provider: {provider}"
