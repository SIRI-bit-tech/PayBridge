from rest_framework.exceptions import APIException
from rest_framework import status


class PayBridgeException(APIException):
    """Base exception for PayBridge API"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred'
    default_code = 'error'


class InvalidAPIKey(PayBridgeException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired API key'
    default_code = 'invalid_api_key'


class RateLimitExceeded(PayBridgeException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'rate_limit_exceeded'


class KYCVerificationFailed(PayBridgeException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'KYC verification failed'
    default_code = 'kyc_verification_failed'


class PaymentProviderError(PayBridgeException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Payment provider error'
    default_code = 'provider_error'


class WebhookDeliveryFailed(PayBridgeException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Webhook delivery failed'
    default_code = 'webhook_delivery_failed'


class SubscriptionRequired(PayBridgeException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Subscription required for this action'
    default_code = 'subscription_required'
