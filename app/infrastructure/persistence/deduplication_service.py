"""
Deduplication Service (Redis-Backed)
=====================================
Ensures idempotency for tracking events using Upstash Redis.
Uses the shared RedisProvider singleton — no direct connection creation.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from app.infrastructure.cache.redis_provider import redis_provider
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class DeduplicationService:
    """
    Redis-backed deduplication and visitor caching.
    
    Key prefixes:
    - evt:{event_id}  — Event dedup (SETNX with TTL)
    - vis:{external_id} — Visitor cache
    """

    def try_consume_event(self, event_id: str, event_name: str = "event", ttl: int = 86400) -> bool:
        """
        Attempt to consume (process) an event ID (Sync).
        Returns True if NEW, False if DUPLICATE.
        """
        if not event_id:
            return True

        redis = redis_provider.sync_client
        if not redis:
            return True  # No Redis → process everything

        key = f"evt:{event_id}"
        try:
            val = str(int(time.time()))
            result = redis.set(key, val, ex=ttl, nx=True)
            if result:
                return True
            else:
                logger.info(f"🛑 Duplicate detected: {key}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Redis dedup error: {e}")
            return True  # Fail-open

    async def try_consume_event_async(self, event_id: str, event_name: str = "event", ttl: int = 86400) -> bool:
        """
        Attempt to consume (process) an event ID (Async).
        Returns True if NEW, False if DUPLICATE.
        """
        if not event_id:
            return True

        redis = redis_provider.async_client
        if not redis:
            return True

        key = f"evt:{event_id}"
        try:
            val = str(int(time.time()))
            result = await redis.set(key, val, ex=ttl, nx=True)
            if result:
                return True
            else:
                logger.info(f"🛑 Duplicate detected (Async): {key}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Redis async dedup error: {e}")
            return True

    def cache_visitor(self, external_id: str, data: dict, ttl: int = 86400):
        """Cache resolved visitor data for subsequent requests."""
        redis = redis_provider.sync_client
        if not redis or not external_id:
            return

        key = f"vis:{external_id}"
        try:
            redis.set(key, json.dumps(data), ex=ttl)
        except Exception as e:
            logger.warning(f"⚠️ Redis cache_visitor error: {e}")

    async def cache_visitor_async(self, external_id: str, data: dict, ttl: int = 86400):
        """Cache resolved visitor data for subsequent requests (Async)."""
        redis = redis_provider.async_client
        if not redis or not external_id:
            return

        key = f"vis:{external_id}"
        try:
            await redis.set(key, json.dumps(data), ex=ttl)
        except Exception as e:
            logger.warning(f"⚠️ Redis async cache_visitor error: {e}")

    def get_visitor(self, external_id: str) -> Optional[dict]:
        """Get cached visitor data."""
        redis = redis_provider.sync_client
        if not redis or not external_id:
            return None

        key = f"vis:{external_id}"
        try:
            data = redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"⚠️ Redis get_visitor error: {e}")
        return None

    async def get_visitor_async(self, external_id: str) -> Optional[dict]:
        """Get cached visitor data (Async)."""
        redis = redis_provider.async_client
        if not redis or not external_id:
            return None

        key = f"vis:{external_id}"
        try:
            data = await redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"⚠️ Redis async get_visitor error: {e}")
        return None


# Singleton Instance
dedup_service = DeduplicationService()
