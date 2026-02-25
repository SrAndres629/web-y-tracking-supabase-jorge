"""
🧠 Cache Utilities — shared Redis wrapper for CMS and general caching.

Uses the shared RedisProvider singleton. No direct Upstash connections.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

from app.infrastructure.cache.redis_provider import redis_provider
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """JSON cache wrapper using the shared RedisProvider."""

    async def get_json(self, key: str) -> Optional[Any]:
        redis = redis_provider.sync_client
        if not redis:
            return None
        try:
            data = redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug("Redis get error: %s", e)
        return None

    async def set_json(self, key: str, value: Any, expire: int = 3600) -> None:
        redis = redis_provider.sync_client
        if not redis:
            return
        try:
            redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.debug("Redis set error: %s", e)

    async def delete(self, key: str) -> None:
        redis = redis_provider.sync_client
        if not redis:
            return
        try:
            redis.delete(key)
        except Exception as e:
            logger.debug("Redis delete error: %s", e)


redis_cache = RedisCache()

REDIS_ENABLED = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)

# ── Backwards-compatible dedup API (used by tests) ──────────────
# When REDIS_ENABLED is False (or patched in tests), fallback to in-memory.
_memory_cache: Dict[str, float] = {}


def deduplicate_event(event_id: str, event_name: str = "event", ttl: int = 86400) -> bool:
    """
    Returns True if the event is NEW (first seen), False if duplicate.

    Uses Redis when available, in-memory dict otherwise.
    """
    cache_key = f"evt:{event_id}"

    if REDIS_ENABLED:
        redis = redis_provider.sync_client
        if redis:
            try:
                result = redis.set(cache_key, str(int(time.time())), ex=ttl, nx=True)
                return result is not None
            except Exception as e:
                logger.warning(f"Redis dedup error: {e}")
                # Fall through to memory

    # In-memory fallback
    now = time.time()
    if cache_key in _memory_cache:
        if now - _memory_cache[cache_key] < ttl:
            return False  # Duplicate
    _memory_cache[cache_key] = now
    return True  # New event


def redis_health_check() -> Dict[str, Any]:
    """Check if Redis is configured and reachable."""
    return redis_provider.health_check()
