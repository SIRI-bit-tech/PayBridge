from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Transaction, Settlement
import logging

logger = logging.getLogger(__name__)


class SettlementViewSet(viewsets.ViewSet):
    """Settlement and balance management"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current balance and settlement information"""
        user = request.user
        
        # Calculate available balance (completed transactions older than 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        available_txns = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__lte=seven_days_ago
        ).aggregate(total=Sum('net_amount'))
        
        # Calculate pending balance (completed transactions within last 7 days)
        pending_txns = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__gt=seven_days_ago
        ).aggregate(total=Sum('net_amount'))
        
        # Get last settlement
        last_settlement = Settlement.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()
        
        # Calculate next settlement date (every Monday)
        today = timezone.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_settlement = today + timedelta(days=days_until_monday)
        
        return Response({
            'available_balance': float(available_txns['total'] or Decimal('0')),
            'pending_balance': float(pending_txns['total'] or Decimal('0')),
            'currency': 'NGN',  # Default currency, should be user's preferred currency
            'next_settlement_date': next_settlement.isoformat(),
            'last_settlement_date': last_settlement.created_at.isoformat() if last_settlement else None,
            'last_settlement_amount': float(last_settlement.amount) if last_settlement else None,
        })
    
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Initiate a withdrawal/settlement"""
        user = request.user
        
        # Calculate available balance
        seven_days_ago = timezone.now() - timedelta(days=7)
        available_txns = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__lte=seven_days_ago
        ).aggregate(total=Sum('net_amount'))
        
        available_balance = available_txns['total'] or Decimal('0')
        
        if available_balance <= 0:
            return Response(
                {'error': 'No available balance for withdrawal'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create settlement record
        settlement = Settlement.objects.create(
            user=user,
            amount=available_balance,
            currency='NGN',
            status='pending',
            bank_account=user.profile.bank_account if hasattr(user, 'profile') else None
        )
        
        # In production, this would trigger actual bank transfer
        # For now, we'll mark it as processing
        logger.info(f"Settlement initiated for user {user.email}: {available_balance}")
        
        return Response({
            'id': str(settlement.id),
            'amount': float(settlement.amount),
            'currency': settlement.currency,
            'status': settlement.status,
            'message': 'Withdrawal initiated successfully. Funds will be transferred within 1-2 business days.'
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get settlement history"""
        user = request.user
        settlements = Settlement.objects.filter(user=user).order_by('-created_at')[:20]
        
        data = [{
            'id': str(s.id),
            'amount': float(s.amount),
            'currency': s.currency,
            'status': s.status,
            'created_at': s.created_at.isoformat(),
            'completed_at': s.completed_at.isoformat() if s.completed_at else None,
        } for s in settlements]
        
        return Response(data)
