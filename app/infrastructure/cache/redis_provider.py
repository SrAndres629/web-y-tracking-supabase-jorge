"""
🔌 Redis Provider — Single Source of Truth for Upstash Redis connections.

All Redis consumers MUST use this provider instead of creating their own
connections. This ensures:
- Single TCP connection shared across the application
- Consistent configuration from settings
- Graceful fallback when Redis is unavailable

Usage:
    from app.infrastructure.cache.redis_provider import redis_provider
    
    # Sync
    client = redis_provider.sync_client
    if client:
        client.set("key", "value", ex=3600)
    
    # Async
    client = redis_provider.async_client
    if client:
        await client.set("key", "value", ex=3600)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class RedisProvider:
    """
    Singleton provider for Upstash Redis connections.
    
    Provides both sync and async clients, initialized lazily
    on first access. All modules should import `redis_provider`
    instead of creating their own Redis instances.
    """

    def __init__(self) -> None:
        self._sync_client: Any = None
        self._async_client: Any = None
        self._initialized = False
        self._available = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization — only connect when first accessed."""
        if self._initialized:
            return
        self._initialized = True

        if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
            logger.info("⚡ RedisProvider: No Upstash credentials — running in memory-only mode")
            return

        try:
            from upstash_redis import Redis
            from upstash_redis.asyncio import Redis as AsyncRedis

            self._sync_client = Redis(
                url=settings.UPSTASH_REDIS_REST_URL,
                token=settings.UPSTASH_REDIS_REST_TOKEN,
            )
            self._async_client = AsyncRedis(
                url=settings.UPSTASH_REDIS_REST_URL,
                token=settings.UPSTASH_REDIS_REST_TOKEN,
            )
            self._available = True
            logger.info("✅ RedisProvider: Connected to Upstash (Sync + Async)")

        except ImportError:
            logger.warning("⚠️ RedisProvider: upstash-redis not installed")
        except Exception as e:
            logger.exception(f"❌ RedisProvider: Connection failed: {e}")

    @property
    def sync_client(self) -> Any:
        """Get the synchronous Redis client (or None if unavailable)."""
        self._ensure_initialized()
        return self._sync_client

    @property
    def async_client(self) -> Any:
        """Get the async Redis client (or None if unavailable)."""
        self._ensure_initialized()
        return self._async_client

    @property
    def is_available(self) -> bool:
        """Check if Redis is connected and operational."""
        self._ensure_initialized()
        return self._available

    def health_check(self) -> dict:
        """Perform a health check on the Redis connection."""
        if not self.is_available:
            return {"status": "disabled", "reason": "No credentials or connection failed"}
        try:
            self._sync_client.ping()
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ═══════════════════════════════════════════
# SINGLETON — Import this, not the class
# ═══════════════════════════════════════════
redis_provider = RedisProvider()
