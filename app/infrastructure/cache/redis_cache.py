"""Redis cache layer with async-friendly wrappers."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable

from app.application.interfaces.cache_port import DeduplicationPort
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class RedisDeduplication(DeduplicationPort):
    """Deduplicación usando Redis SET NX con wrappers async."""

    DEFAULT_TTL_SECONDS = 86400

    def __init__(self, redis_client=None):
        self._client = redis_client
        self._settings = get_settings()

    @property
    def _redis(self):
        if self._client is None:
            try:
                from upstash_redis import Redis

                if self._settings.redis.is_configured:
                    self._client = Redis(
                        url=str(self._settings.redis.rest_url),
                        token=str(self._settings.redis.rest_token),
                    )
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        return self._client

    async def _call_redis(self, func: Callable, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def is_unique(self, event_key: str) -> bool:
        if not self._redis:
            return True

        try:
            cache_key = f"dedup:{event_key}"
            result = await self._call_redis(
                self._redis.set,
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
        if not self._redis:
            return

        try:
            cache_key = f"dedup:{event_key}"
            await self._call_redis(
                self._redis.set,
                cache_key,
                "1",
                ex=ttl_seconds,
            )
        except Exception as e:
            logger.warning(f"Redis mark_processed error: {e}")
