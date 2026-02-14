"""
📡 Tracker Port - Interface para trackers externos.

Implementaciones:
- MetaTracker (Meta CAPI)
- RudderStackTracker
- WebhookTracker (n8n)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.events import TrackingEvent
from app.domain.models.visitor import Visitor


class TrackerPort(ABC):
    """
    Puerto para trackers de eventos externos.
    
    Cada implementación envía eventos a un servicio diferente.
    La aplicación los usa indistintamente via polimorfismo.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador del tracker."""
        raise NotImplementedError
    
    @abstractmethod
    async def track(self, event: TrackingEvent, visitor: Visitor) -> bool:
        """
        Envia evento al tracker externo.
        
        Args:
            event: Evento de tracking
            visitor: Visitante asociado (para datos adicionales)
            
        Returns:
            True si se envió exitosamente, False si falló.
            
        Note:
            No debe lanzar excepciones - errores se loguean internamente.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifica conectividad con el servicio.
        
        Returns:
            True si el servicio está disponible.
        """
        raise NotImplementedError
