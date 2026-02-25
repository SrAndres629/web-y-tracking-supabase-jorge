"""Redis dedup implementation of the DDD DeduplicationPort."""

from __future__ import annotations

import asyncio
import logging

from app.application.interfaces.cache_port import DeduplicationPort
from app.infrastructure.cache.redis_provider import redis_provider

logger = logging.getLogger(__name__)


class RedisDeduplication(DeduplicationPort):
    """
    Deduplicación usando Redis SET NX — consistent `evt:` key prefix.
    
    Uses the shared RedisProvider singleton.
    """

    DEFAULT_TTL_SECONDS = 86400

    async def is_unique(self, event_key: str) -> bool:
        redis = redis_provider.async_client
        if not redis:
            return True  # No Redis → process everything

        try:
            cache_key = f"evt:{event_key}"
            result = await redis.set(
                cache_key,
                "1",
                nx=True,
                ex=self.DEFAULT_TTL_SECONDS,
            )
            is_new = result is not None
            if not is_new:
                logger.debug(f"🔄 Duplicate event detected: {event_key}")
            return is_new
        except Exception as e:
            logger.warning(f"Redis dedup error: {e}")
            return True

    async def mark_processed(self, event_key: str, ttl_seconds: int = 86400) -> None:
        redis = redis_provider.async_client
        if not redis:
            return

        try:
            cache_key = f"evt:{event_key}"
            await redis.set(
                cache_key,
                "1",
                ex=ttl_seconds,
            )
        except Exception as e:
            logger.warning(f"Redis mark_processed error: {e}")
