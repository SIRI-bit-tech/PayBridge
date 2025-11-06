import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import PaymentProvider
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_connect_account(request):
    """Create Stripe Connect account for user"""
    stripe.api_key = settings.STRIPE_API_KEY
    
    try:
        country = request.data.get('country', 'US')
        business_type = request.data.get('business_type', 'individual')
        
        account = stripe.Account.create(
            type='standard',
            country=country,
            email=request.user.email,
            business_type=business_type,
        )
        
        # Store Stripe account ID
        PaymentProvider.objects.update_or_create(
            user=request.user,
            provider='stripe_connect',
            defaults={
                'public_key': account.id,
                'secret_key': account.id,
                'is_active': True,
                'webhook_url': f"{settings.ALLOWED_HOSTS[0]}/webhooks/stripe/"
            }
        )
        
        return Response({
            'success': True,
            'account_id': account.id,
            'onboarding_url': f"https://connect.stripe.com/express/start/{account.id}"
        })
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe Connect error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stripe_connect_status(request):
    """Get Stripe Connect account status"""
    stripe.api_key = settings.STRIPE_API_KEY
    
    provider = PaymentProvider.objects.filter(
        user=request.user,
        provider='stripe_connect'
    ).first()
    
    if not provider:
        return Response({'connected': False})
    
    try:
        account = stripe.Account.retrieve(provider.public_key)
        
        return Response({
            'connected': True,
            'account_id': account.id,
            'charges_enabled': account.charges_enabled,
            'payouts_enabled': account.payouts_enabled,
            'requirements': account.requirements if hasattr(account, 'requirements') else {}
        })
    
    except stripe.error.StripeError as e:
        logger.error(f"Error fetching Stripe account: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_connect_payment(request):
    """Create payment using Stripe Connect"""
    stripe.api_key = settings.STRIPE_API_KEY
    
    provider = PaymentProvider.objects.filter(
        user=request.user,
        provider='stripe_connect'
    ).first()
    
    if not provider:
        return Response({
            'error': 'Stripe Connect not configured'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = int(float(request.data.get('amount', 0)) * 100)
        currency = request.data.get('currency', 'usd').lower()
        description = request.data.get('description', 'Payment via PayBridge')
        
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            stripe_account=provider.public_key,
        )
        
        return Response({
            'success': True,
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id
        })
    
    except stripe.error.StripeError as e:
        logger.error(f"Payment error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
