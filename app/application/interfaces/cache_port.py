"""
💾 Cache Port - Interface para sistemas de cache.

Implementaciones:
- RedisDeduplication (producción)
- InMemoryDeduplication (desarrollo/testing)
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class DeduplicationPort(ABC):
    """
    Puerto para deduplicación de eventos.

    Responsabilidad: Determinar si un evento ya fue procesado.
    """

    @abstractmethod
    async def is_unique(self, event_key: str) -> bool:
        """
        Verifica si el evento es único (no procesado antes).

        Args:
            event_key: Identificador único del evento

        Returns:
            True si es nuevo (debe procesarse), False si es duplicado.

        Side effect: Marca el evento como procesado si es nuevo.
        """
        raise NotImplementedError

    @abstractmethod
    async def mark_processed(self, event_key: str, ttl_seconds: int = 86400) -> None:
        """
        Marca evento como procesado manualmente.

        Args:
            event_key: Identificador del evento
            ttl_seconds: Tiempo de vida del registro (default 24h)
        """
        raise NotImplementedError
