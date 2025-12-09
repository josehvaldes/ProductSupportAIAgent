
import json
from threading import RLock
import traceback
import redis.asyncio as aioredis

from shopassist_api.application.interfaces.service_interfaces import CacheServiceInterface
from shopassist_api.application.settings.config import settings
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class RedisCacheService(CacheServiceInterface):
    """Service for caching using Redis"""
    
    _client = None
    _client_lock = RLock()

    def __init__(self):
        self.client = None
        self._initialize_client()
        self.client = RedisCacheService._client

    def _initialize_client(self):
        """Initialize the Redis client."""

        if RedisCacheService._client is None:
            with RedisCacheService._client_lock:
                # Double-check after acquiring lock
                if RedisCacheService._client is None:
                    logger.info(f"Initializing singleton Redis client [{settings.redis_url}]")
                    RedisCacheService._client = aioredis.from_url(
                        settings.redis_url,
                        password=settings.redis_password,
                        decode_responses=True
                    )
                else:
                    logger.info("Using existing singleton Redis client")
        
    async def get(self, key: str) -> str:
        """Get value from cache by key"""
        value = await self.client.get(key)
        if value:
            return value
        return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache with optional TTL (default 1 hour)"""
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache by key"""
        await self.client.delete(key)

    async def health_check(self) -> bool:
        """Ping the Redis service to check connectivity"""
        try:
            if not self.client:
                return False
            pong = await self.client.ping()
            return pong
        except Exception:
            trace = traceback.format_exc()
            logger.error(f"Redis health check failed: {trace}")
            return False