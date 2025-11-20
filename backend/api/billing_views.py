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


# Webhook handlers moved to webhook_receiver.py
# These old billing-specific webhook handlers are deprecated
# The new webhook system in webhook_receiver.py handles all provider webhooks
# and processes billing events through webhook_tasks.py
