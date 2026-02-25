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


def redis_health_check() -> Dict[str, Any]:
    """Check if Redis is configured and reachable."""
    return redis_provider.health_check()
