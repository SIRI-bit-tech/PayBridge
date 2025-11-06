import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    """Real-time dashboard updates via WebSocket"""
    
    async def connect(self):
        """Initialize WebSocket connection"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_group_name = f"dashboard_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.email} connected to dashboard")
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"User disconnected from dashboard")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_analytics':
                await self.send_analytics()
            elif message_type == 'subscribe_transactions':
                await self.send_latest_transactions()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def analytics_update(self, event):
        """Send analytics update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'analytics',
            'data': event['data']
        }))
    
    async def transaction_update(self, event):
        """Send transaction update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'transaction',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def send_analytics(self):
        """Get and send current analytics"""
        from api.models import Transaction
        from django.db.models import Sum, Count, Avg
        
        stats = Transaction.objects.filter(
            user=self.user
        ).aggregate(
            total_transactions=Count('id'),
            total_volume=Sum('amount'),
            avg_transaction=Avg('amount'),
            successful=Count('id', filter=models.Q(status='completed'))
        )
        
        return stats
    
    async def send_analytics_async(self):
        """Send analytics to client"""
        stats = await self.send_analytics()
        
        await self.send(text_data=json.dumps({
            'type': 'analytics',
            'data': {
                'total_transactions': stats['total_transactions'] or 0,
                'total_volume': str(stats['total_volume'] or 0),
                'avg_transaction': str(stats['avg_transaction'] or 0),
                'success_rate': (
                    (stats['successful'] / stats['total_transactions'] * 100)
                    if stats['total_transactions'] else 0
                )
            }
        }))
    
    @database_sync_to_async
    def get_latest_transactions(self):
        """Get latest transactions for user"""
        from api.models import Transaction
        
        return list(Transaction.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10].values(
            'id', 'reference', 'amount', 'currency', 
            'status', 'provider', 'created_at'
        ))
    
    async def send_latest_transactions(self):
        """Send latest transactions to client"""
        transactions = await self.get_latest_transactions()
        
        await self.send(text_data=json.dumps({
            'type': 'transactions',
            'data': [
                {
                    **t,
                    'amount': str(t['amount']),
                    'created_at': t['created_at'].isoformat()
                }
                for t in transactions
            ]
        }))


class TransactionConsumer(AsyncWebsocketConsumer):
    """Real-time transaction status updates"""
    
    async def connect(self):
        """Initialize transaction status connection"""
        self.transaction_id = self.scope['url_route']['kwargs']['transaction_id']
        self.room_group_name = f"transaction_{self.transaction_id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def transaction_status(self, event):
        """Send transaction status update"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'data': event['data']
        }))
