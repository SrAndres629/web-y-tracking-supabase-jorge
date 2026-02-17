"""
🧠 Legacy Cache Utilities (Compat Layer).

This module keeps legacy call sites working while the
Clean/DDD cache implementations live in app.infrastructure.cache.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class LegacyRedisCache:
    """Simple JSON cache wrapper for legacy services."""

    def __init__(self):
        self._client = None

    @property
    def _redis(self):
        if self._client is None:
            try:
                from upstash_redis import Redis

                if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
                    self._client = Redis(
                        url=settings.UPSTASH_REDIS_REST_URL,
                        token=settings.UPSTASH_REDIS_REST_TOKEN,
                    )
            except Exception as e:
                logger.debug(f"Redis not available: {e}")
        return self._client

    async def get_json(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Redis get error: {e}")
        return None

    async def set_json(self, key: str, value: Any, expire: int = 3600) -> None:
        if not self._redis:
            return
        try:
            self._redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.debug(f"Redis set error: {e}")

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            self._redis.delete(key)
        except Exception as e:
            logger.debug(f"Redis delete error: {e}")


redis_cache = LegacyRedisCache()

REDIS_ENABLED = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)


# In-memory fallback for dedup & visitor cache
_memory_cache: Dict[str, float] = {}
_visitor_cache: Dict[str, Dict[str, Any]] = {}


def deduplicate_event(event_id: str, event_name: str = "event", ttl_hours: int = 24) -> bool:
    """
    Returns True if event is unique (not seen), False if duplicate.
    """
    key = f"evt:{event_id}"
    now = time.time()
    expires = _memory_cache.get(key)
    if expires and expires > now:
        return False
    _memory_cache[key] = now + ttl_hours * 3600
    return True


def cache_visitor_data(external_id: str, data: Dict[str, Any], ttl_hours: int = 24) -> None:
    """Cache visitor data for quick identity resolution."""
    _visitor_cache[external_id] = {"data": data, "expires": time.time() + ttl_hours * 3600}


def get_cached_visitor(external_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached visitor data if still valid."""
    item = _visitor_cache.get(external_id)
    if not item:
        return None
    if item["expires"] < time.time():
        _visitor_cache.pop(external_id, None)
        return None
    return item["data"]


def redis_health_check() -> Dict[str, Any]:
    """Check if Redis is configured and reachable."""
    if not (settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN):
        return {"status": "disabled"}
    try:
        # best-effort ping
        if redis_cache._redis:
            redis_cache._redis.ping()
            return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "unknown"}
