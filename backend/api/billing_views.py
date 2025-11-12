"""
Billing API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import logging
from .billing_models import Plan, BillingSubscription, Payment
from .billing_subscription_service import BillingSubscriptionService
from .usage_tracking_service import UsageTrackingService
from .payment_providers import get_payment_provider

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_billing_plan(request):
    """Get current subscription and available plans"""
    try:
        user = request.user
        
        # Get user subscription info
        subscription_info = BillingSubscriptionService.get_user_subscription_info(user)
        
        if not subscription_info:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all available plans
        plans = Plan.objects.filter(is_active=True).order_by('price')
        available_plans = []
        
        for plan in plans:
            available_plans.append({
                'id': str(plan.id),
                'name': plan.name,
                'tier': plan.tier,
                'price': float(plan.price),
                'currency': plan.currency,
                'duration': plan.duration,
                'api_limit': plan.api_limit,
                'webhook_limit': plan.webhook_limit,
                'has_analytics': plan.has_analytics,
                'analytics_level': plan.analytics_level,
                'has_priority_support': plan.has_priority_support,
                'has_custom_branding': plan.has_custom_branding,
            })
        
        return Response({
            'current_subscription': subscription_info['subscription'],
            'usage': subscription_info['usage'],
            'available_plans': available_plans,
        })
        
    except Exception as e:
        logger.error(f"Error getting billing plan: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create payment session for subscription upgrade"""
    try:
        user = request.user
        plan_id = request.data.get('plan_id')
        provider = request.data.get('provider', 'stripe')
        
        if not plan_id:
            return Response(
                {'error': 'plan_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if provider not in ['paystack', 'flutterwave', 'stripe']:
            return Response(
                {'error': 'Invalid payment provider'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment session
        result = BillingSubscriptionService.create_payment_session(
            user, plan_id, provider
        )
        
        if not result['success']:
            return Response(
                {'error': result.get('error', 'Failed to create payment session')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel user subscription"""
    try:
        user = request.user
        
        result = BillingSubscriptionService.cancel_subscription(user)
        
        if not result['success']:
            return Response(
                {'error': result.get('error', 'Failed to cancel subscription')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': 'Subscription cancelled successfully'})
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_usage(request):
    """Get current usage statistics"""
    try:
        user = request.user
        
        usage = UsageTrackingService.get_current_usage(user)
        
        if not usage:
            return Response(
                {'error': 'Usage data not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(usage)
        
    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    """Get user payment history"""
    try:
        user = request.user
        
        payments = Payment.objects.filter(user=user).order_by('-created_at')[:20]
        
        payment_list = []
        for payment in payments:
            payment_list.append({
                'id': str(payment.id),
                'amount': float(payment.amount),
                'currency': payment.currency,
                'status': payment.status,
                'provider': payment.provider,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at.isoformat(),
                'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
            })
        
        return Response({'payments': payment_list})
        
    except Exception as e:
        logger.error(f"Error getting payment history: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def webhook_paystack(request):
    """Handle Paystack webhook"""
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Paystack-Signature')
        if not signature:
            return Response(
                {'error': 'No signature provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider = get_payment_provider('paystack')
        if not provider.verify_webhook_signature(request.body, signature):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Process webhook event
        event = request.data.get('event')
        data = request.data.get('data', {})
        
        if event == 'charge.success':
            reference = data.get('reference')
            if reference:
                result = BillingSubscriptionService.confirm_payment_and_upgrade(
                    reference, 'paystack'
                )
                logger.info(f"Paystack webhook processed: {reference}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing Paystack webhook: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def webhook_flutterwave(request):
    """Handle Flutterwave webhook"""
    try:
        # Verify webhook signature
        signature = request.headers.get('verif-hash')
        if not signature:
            return Response(
                {'error': 'No signature provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider = get_payment_provider('flutterwave')
        if not provider.verify_webhook_signature(request.body, signature):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Process webhook event
        event = request.data.get('event')
        data = request.data.get('data', {})
        
        if event == 'charge.completed':
            tx_ref = data.get('tx_ref')
            if tx_ref:
                result = BillingSubscriptionService.confirm_payment_and_upgrade(
                    tx_ref, 'flutterwave'
                )
                logger.info(f"Flutterwave webhook processed: {tx_ref}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing Flutterwave webhook: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def webhook_stripe(request):
    """Handle Stripe webhook"""
    try:
        # Verify webhook signature
        signature = request.headers.get('Stripe-Signature')
        if not signature:
            return Response(
                {'error': 'No signature provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider = get_payment_provider('stripe')
        if not provider.verify_webhook_signature(request.body, signature):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Process webhook event
        event_type = request.data.get('type')
        data = request.data.get('data', {}).get('object', {})
        
        if event_type == 'payment_intent.succeeded':
            payment_intent_id = data.get('id')
            if payment_intent_id:
                result = BillingSubscriptionService.confirm_payment_and_upgrade(
                    payment_intent_id, 'stripe'
                )
                logger.info(f"Stripe webhook processed: {payment_intent_id}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
