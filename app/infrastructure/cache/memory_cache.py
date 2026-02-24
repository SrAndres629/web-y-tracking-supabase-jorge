"""
🧠 In-Memory Cache Implementation.

Para desarrollo local y testing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from app.application.interfaces.cache_port import DeduplicationPort


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
