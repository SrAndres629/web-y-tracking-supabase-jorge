"""
💾 Cache Port - Interface para sistemas de cache.

Implementaciones:
- RedisDeduplication (producción)
- InMemoryDeduplication (desarrollo/testing)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


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


class ContentCachePort(ABC):
    """
    Puerto para cache de contenido.
    
    Responsabilidad: Almacenar y recuperar contenido dinámico.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor del cache.
        
        Args:
            key: Clave del contenido
            
        Returns:
            Valor cacheado o None si no existe/expiró.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> None:
        """
        Guarda valor en cache.
        
        Args:
            key: Clave del contenido
            value: Valor a cachear (debe ser serializable)
            ttl: Tiempo de vida en segundos
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Elimina valor del cache."""
        raise NotImplementedError
    
    @abstractmethod
    async def clear(self) -> None:
        """Limpia todo el cache."""
        raise NotImplementedError
