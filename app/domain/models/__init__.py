"""
🧩 Domain Models - Entidades y Value Objects.

Estos modelos son PUROS:
- No dependen de frameworks
- No tienen métodos de persistencia
- Representan el negocio tal cual es
"""

from app.domain.models.events import EventName, TrackingEvent
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Email, EventId, ExternalId, Phone
from app.domain.models.visitor import Visitor, VisitorSource

__all__ = [
    # Value Objects
    "EventId",
    "ExternalId",
    "Phone",
    "Email",
    # Entities
    "Visitor",
    "VisitorSource",
    "Lead",
    "LeadStatus",
    "TrackingEvent",
    "EventName",
]
