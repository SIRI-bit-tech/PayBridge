"""
Redis Listener for Settings Events
Listens to settings_updates and provider_updates channels
"""
import json
import logging
import asyncio
from typing import Dict, Any
from .socketio_server import (
    sio, emit_profile_updated, emit_provider_updated,
    emit_provider_added, emit_provider_deleted, emit_provider_mode_changed
)

logger = logging.getLogger(__name__)

# Redis channels
SETTINGS_UPDATES_CHANNEL = 'settings_updates'
PROVIDER_UPDATES_CHANNEL = 'provider_updates'


class SettingsRedisListener:
    """Redis listener for settings events"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
    
    async def connect(self):
        """Connect to Redis and subscribe to channels"""
        try:
            import redis.asyncio as aioredis
            import os
            from urllib.parse import quote_plus
            
            # Redis configuration
            REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
            REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
            REDIS_DB = int(os.getenv('REDIS_DB', 0))
            REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
            
            # Create async Redis client
            if REDIS_PASSWORD:
                encoded_password = quote_plus(REDIS_PASSWORD)
                redis_url = f"redis://:{encoded_password}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
            else:
                redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
            
            self.redis_client = await aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Create pubsub instance
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to channels
            await self.pubsub.subscribe(SETTINGS_UPDATES_CHANNEL)
            await self.pubsub.subscribe(PROVIDER_UPDATES_CHANNEL)
            
            logger.info("Settings Redis listener connected and subscribed")
        except Exception as e:
            logger.exception(f"Failed to connect settings Redis listener: {str(e)}")
            self.redis_client = None
            self.pubsub = None
    
    async def listen(self):
        """Listen for Redis pub/sub messages"""
        logger.info("Starting settings Redis listener...")
        
        while True:
            try:
                # Ensure we're connected
                if not self.pubsub:
                    logger.warning("Redis pubsub not available, attempting to connect...")
                    await self.connect()
                    if not self.pubsub:
                        logger.error("Failed to connect to Redis, retrying in 5 seconds...")
                        await asyncio.sleep(5)
                        continue
                
                # Listen for messages
                async for message in self.pubsub.listen():
                    if message['type'] == 'message':
                        await self._handle_message(message)
                        
            except Exception:
                logger.error("Error in settings Redis listener")
                # Clean up connection on error
                self.pubsub = None
                self.redis_client = None
                # Wait 5 seconds before retrying
                await asyncio.sleep(5)
                logger.info("Attempting to reconnect settings Redis listener...")
    
    async def _handle_message(self, message):
        """Handle incoming Redis message"""
        try:
            channel = message['channel']
            data = json.loads(message['data'])
            
            if channel == SETTINGS_UPDATES_CHANNEL:
                await self._handle_settings_event(data)
            elif channel == PROVIDER_UPDATES_CHANNEL:
                await self._handle_provider_event(data)
        except Exception as e:
            logger.error(f"Error handling settings Redis message: {str(e)}")
    
    async def _handle_settings_event(self, data):
        """Handle settings update event from Redis"""
        event_type = data.get('type')
        user_id = data.get('user_id')
        event_data = data.get('data')
        
        if not all([event_type, user_id, event_data]):
            logger.warning("Invalid settings event data")
            return
        
        if event_type == 'profile_updated':
            await emit_profile_updated(user_id, event_data)
            logger.info(f"Emitted profile_updated for user {user_id} from Redis")
    
    async def _handle_provider_event(self, data):
        """Handle provider update event from Redis"""
        event_type = data.get('type')
        user_id = data.get('user_id')
        event_data = data.get('data')
        
        if not all([event_type, user_id, event_data]):
            logger.warning("Invalid provider event data")
            return
        
        if event_type == 'provider_added':
            await emit_provider_added(user_id, event_data)
            logger.info(f"Emitted provider_added for user {user_id} from Redis")
        elif event_type == 'provider_updated':
            await emit_provider_updated(user_id, event_data)
            logger.info(f"Emitted provider_updated for user {user_id} from Redis")
        elif event_type == 'provider_deleted':
            await emit_provider_deleted(user_id, event_data)
            logger.info(f"Emitted provider_deleted for user {user_id} from Redis")
        elif event_type == 'provider_mode_changed':
            await emit_provider_mode_changed(user_id, event_data)
            logger.info(f"Emitted provider_mode_changed for user {user_id} from Redis")
        elif event_type == 'provider_primary_changed':
            await emit_provider_updated(user_id, event_data)
            logger.info(f"Emitted provider_primary_changed for user {user_id} from Redis")


# Global listener instance
settings_redis_listener = SettingsRedisListener()
