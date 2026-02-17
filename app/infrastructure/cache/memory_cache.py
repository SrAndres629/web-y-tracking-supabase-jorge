"""
🧠 In-Memory Cache Implementation.

Para desarrollo local y testing.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.application.interfaces.cache_port import ContentCachePort, DeduplicationPort

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache con TTL."""

    value: Any
    expires_at: float


class InMemoryDeduplication(DeduplicationPort):
    """Deduplicación en memoria (para testing)."""

    def __init__(self):
        self._store: Dict[str, CacheEntry] = {}

    async def is_unique(self, event_key: str) -> bool:
        """Verifica unicidad en memoria."""
        now = time.time()
        cache_key = f"dedup:{event_key}"

        # Limpiar expirados
        self._cleanup_expired(now)

        if cache_key in self._store:
            entry = self._store[cache_key]
            if entry.expires_at > now:
                return False  # Ya existe y no expiró

        # Marcar como procesado
        self._store[cache_key] = CacheEntry(
            value=True,
            expires_at=now + 86400,  # 24 horas
        )
        return True

    async def mark_processed(self, event_key: str, ttl_seconds: int = 86400) -> None:
        """Marca evento como procesado."""
        self._store[f"dedup:{event_key}"] = CacheEntry(
            value=True,
            expires_at=time.time() + ttl_seconds,
        )

    def _cleanup_expired(self, now: float) -> None:
        """Limpia entradas expiradas."""
        expired = [key for key, entry in self._store.items() if entry.expires_at <= now]
        for key in expired:
            del self._store[key]


class InMemoryContentCache(ContentCachePort):
    """Cache de contenido en memoria."""

    def __init__(self, max_size: int = 100):
        self._store: Dict[str, CacheEntry] = {}
        self._max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache."""
        now = time.time()
        entry = self._store.get(key)

        if entry is None:
            return None

        if entry.expires_at <= now:
            del self._store[key]
            return None

        return entry.value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Guarda valor en cache."""
        # Evict if at capacity
        if len(self._store) >= self._max_size and key not in self._store:
            # Remove oldest entry
            oldest_key = min(self._store, key=lambda k: self._store[k].expires_at)
            del self._store[oldest_key]

        self._store[key] = CacheEntry(
            value=value,
            expires_at=time.time() + ttl,
        )

    async def delete(self, key: str) -> None:
        """Elimina valor del cache."""
        self._store.pop(key, None)

    async def clear(self) -> None:
        """Limpia todo el cache."""
        self._store.clear()
