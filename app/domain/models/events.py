"""
📊 TrackingEvent Entity - Evento de tracking.

Representa una acción del usuario que queremos trackear:
- PageView: Ver página
- ViewContent: Ver servicio específico
- Lead: Click WhatsApp, formulario
- Contact: Contacto iniciado
- etc.

Inmutable (frozen) porque los eventos históricos no cambian.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Self, Any
from enum import Enum, auto

from app.domain.models.values import EventId, ExternalId, UTMParams


class EventName(Enum):
    """Eventos estándar soportados."""
    PAGE_VIEW = "PageView"
    VIEW_CONTENT = "ViewContent"
    LEAD = "Lead"
    CONTACT = "Contact"
    INITIATE_CHECKOUT = "InitiateCheckout"
    PURCHASE = "Purchase"
    COMPLETE_REGISTRATION = "CompleteRegistration"
    SCHEDULE = "Schedule"
    CUSTOMIZE_PRODUCT = "CustomizeProduct"
    
    # Custom events
    SLIDER_INTERACTION = "SliderInteraction"
    WHATSAPP_CLICK = "WhatsAppClick"


@dataclass(frozen=True, slots=True)
class TrackingEvent:
    """
    Value Object: Evento de tracking inmutable.
    
    Los eventos son inmutables porque representan algo
    que ocurrió en un momento específico del tiempo.
    
    Attributes:
        event_id: ID único del evento
        event_name: Tipo de evento
        external_id: ID del visitante
        timestamp: Cuándo ocurrió
        source_url: URL donde ocurrió
        custom_data: Datos específicos del evento
        utm: Parámetros UTM (snapshot al momento del evento)
    """
    event_id: EventId
    event_name: EventName
    external_id: ExternalId
    timestamp: datetime
    source_url: str
    custom_data: dict[str, Any] = field(default_factory=dict)
    utm: UTMParams = field(default_factory=UTMParams)
    
    @classmethod
    def create(
        cls,
        event_name: EventName,
        external_id: ExternalId,
        source_url: str,
        custom_data: Optional[dict[str, Any]] = None,
        utm: Optional[UTMParams] = None,
    ) -> Self:
        """Factory para crear evento nuevo."""
        return cls(
            event_id=EventId.generate(),
            event_name=event_name,
            external_id=external_id,
            timestamp=datetime.utcnow(),
            source_url=source_url,
            custom_data=custom_data or {},
            utm=utm or UTMParams(),
        )
    
    @classmethod
    def reconstruct(
        cls,
        event_id: EventId,
        event_name: EventName,
        external_id: ExternalId,
        timestamp: datetime,
        source_url: str,
        custom_data: Optional[dict[str, Any]] = None,
        utm: Optional[UTMParams] = None,
    ) -> Self:
        """Reconstruye evento desde datos persistidos."""
        return cls(
            event_id=event_id,
            event_name=event_name,
            external_id=external_id,
            timestamp=timestamp,
            source_url=source_url,
            custom_data=custom_data or {},
            utm=utm or UTMParams(),
        )
    
    def with_custom_data(self, **kwargs: Any) -> TrackingEvent:
        """Retorna nuevo evento con datos adicionales (inmutable)."""
        new_data = {**self.custom_data, **kwargs}
        return TrackingEvent(
            event_id=self.event_id,
            event_name=self.event_name,
            external_id=self.external_id,
            timestamp=self.timestamp,
            source_url=self.source_url,
            custom_data=new_data,
            utm=self.utm,
        )
    
    def to_meta_payload(self, visitor) -> dict[str, Any]:
        """
        Convierte a payload para Meta CAPI.
        
        Args:
            visitor: Objeto Visitor con datos adicionales
        """
        from app.core.validators import hash_sha256
        
        payload = {
            "event_name": self.event_name.value,
            "event_time": int(self.timestamp.timestamp()),
            "event_id": self.event_id.value,
            "event_source_url": self.source_url,
            "action_source": "website",
            "user_data": visitor.to_meta_user_data() if visitor else {
                "external_id": hash_sha256(self.external_id.value),
            },
        }
        
        if self.custom_data:
            payload["custom_data"] = self.custom_data
        
        return payload
    
    def is_duplicate_of(self, other: TrackingEvent) -> bool:
        """True si es duplicado (mismo ID)."""
        return self.event_id.value == other.event_id.value
    
    @property
    def is_conversion_event(self) -> bool:
        """True si es evento de conversión (Lead, Purchase, etc)."""
        return self.event_name in [
            EventName.LEAD,
            EventName.CONTACT,
            EventName.PURCHASE,
            EventName.SCHEDULE,
        ]
    
    def __repr__(self) -> str:
        return f"TrackingEvent({self.event_name.value}, {self.event_id})"
