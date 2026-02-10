"""
🔴 Redis Cache Implementation.

Usa Upstash Redis para serverless.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.application.interfaces.cache_port import DeduplicationPort, ContentCachePort
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class RedisDeduplication(DeduplicationPort):
    """Deduplicación usando Redis SET NX (atomic)."""
    
    def __init__(self, redis_client=None):
        self._client = redis_client
        self._settings = get_settings()
    
    @property
    def _redis(self):
        """Lazy load Redis client."""
        if self._client is None:
            try:
                from upstash_redis import Redis
                if self._settings.redis.is_configured:
                    self._client = Redis(
                        url=self._settings.redis.rest_url,
                        token=self._settings.redis.rest_token,
                    )
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        return self._client
    
    async def is_unique(self, event_key: str) -> bool:
        """
        Verifica unicidad usando SET NX (set if not exists).
        
        Retorna True si era nuevo (se seteó), False si ya existía.
        """
        if not self._redis:
            # Fallback: permitir todo
            return True
        
        try:
            cache_key = f"dedup:{event_key}"
            # SET key value NX EX seconds
            result = self._redis.set(
                cache_key,
                "1",
                nx=True,  # Only if not exists
                ex=86400,  # 24 hours TTL
            )
            # SET NX retorna None si ya existía, OK si se seteó
            is_new = result is not None
            if not is_new:
                logger.debug(f"🔄 Duplicate event detected: {event_key}")
            return is_new
            
        except Exception as e:
            logger.error(f"Redis dedup error: {e}")
            # Fail open: permitir si Redis falla
            return True
    
    async def mark_processed(self, event_key: str, ttl_seconds: int = 86400) -> None:
        """Marca evento como procesado."""
        if not self._redis:
            return
        
        try:
            cache_key = f"dedup:{event_key}"
            self._redis.set(cache_key, "1", ex=ttl_seconds)
        except Exception as e:
            logger.error(f"Redis mark_processed error: {e}")


class RedisContentCache(ContentCachePort):
    """Cache de contenido usando Redis."""
    
    def __init__(self, redis_client=None):
        self._client = redis_client
        self._settings = get_settings()
        self._memory_fallback: dict[str, Any] = {}
    
    @property
    def _redis(self):
        """Lazy load Redis client."""
        if self._client is None:
            try:
                from upstash_redis import Redis
                if self._settings.redis.is_configured:
                    self._client = Redis(
                        url=self._settings.redis.rest_url,
                        token=self._settings.redis.rest_token,
                    )
            except Exception as e:
                logger.warning(f"Redis not available, using memory fallback: {e}")
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache."""
        cache_key = f"content:{key}"
        
        if self._redis:
            try:
                data = self._redis.get(cache_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.debug(f"Redis get error: {e}")
        
        # Fallback a memoria
        return self._memory_fallback.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Guarda valor en cache."""
        cache_key = f"content:{key}"
        
        if self._redis:
            try:
                self._redis.set(cache_key, json.dumps(value), ex=ttl)
            except Exception as e:
                logger.debug(f"Redis set error: {e}")
        
        # Siempre guardar en memoria como fallback
        self._memory_fallback[key] = value
    
    async def delete(self, key: str) -> None:
        """Elimina valor del cache."""
        cache_key = f"content:{key}"
        
        if self._redis:
            try:
                self._redis.delete(cache_key)
            except Exception as e:
                logger.debug(f"Redis delete error: {e}")
        
        self._memory_fallback.pop(key, None)
    
    async def clear(self) -> None:
        """Limpia cache de memoria."""
        self._memory_fallback.clear()
