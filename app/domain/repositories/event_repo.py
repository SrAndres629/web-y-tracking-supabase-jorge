"""
📊 Event Repository Interface.

Contrato para persistencia de eventos de tracking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from app.domain.models.events import TrackingEvent, EventName
from app.domain.models.values import EventId, ExternalId


class EventRepository(ABC):
    """
    Repository para TrackingEvent.
    
    Responsabilidades:
    - Persistir eventos (append-only)
    - Búsquedas por external_id, event_name, rango de fechas
    - Deduplicación
    
    Nota: Los eventos son append-only (no se actualizan ni borran).
    """
    
    @abstractmethod
    async def save(self, event: TrackingEvent) -> None:
        """
        Persiste evento.
        
        Si ya existe (mismo event_id), ignora (idempotente).
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, event_id: EventId) -> Optional[TrackingEvent]:
        """Busca evento por ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def list_by_visitor(
        self,
        external_id: ExternalId,
        limit: int = 100,
    ) -> List[TrackingEvent]:
        """
        Lista eventos de un visitante.
        
        Ordenados por timestamp DESC (más reciente primero).
        """
        raise NotImplementedError
    
    @abstractmethod
    async def list_by_visitor_and_type(
        self,
        external_id: ExternalId,
        event_name: EventName,
        limit: int = 50,
    ) -> List[TrackingEvent]:
        """Lista eventos de un tipo específico para un visitante."""
        raise NotImplementedError
    
    @abstractmethod
    async def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        event_name: Optional[EventName] = None,
        limit: int = 1000,
    ) -> List[TrackingEvent]:
        """
        Lista eventos en rango de fechas.
        
        Args:
            start: Fecha inicio
            end: Fecha fin
            event_name: Filtrar por tipo (opcional)
            limit: Límite de resultados
        """
        raise NotImplementedError
    
    @abstractmethod
    async def exists(self, event_id: EventId) -> bool:
        """True si el evento ya existe (para deduplicación)."""
        raise NotImplementedError
    
    @abstractmethod
    async def count_by_visitor(self, external_id: ExternalId) -> int:
        """Cuenta eventos de un visitante."""
        raise NotImplementedError
    
    @abstractmethod
    async def count_by_type_and_date(
        self,
        event_name: EventName,
        date: datetime,
    ) -> int:
        """
        Cuenta eventos de un tipo en una fecha específica.
        
        Útil para métricas diarias.
        """
        raise NotImplementedError


class EventNotFoundError(Exception):
    """Evento no encontrado."""
    pass
