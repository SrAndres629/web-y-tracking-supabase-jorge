"""
📋 Data Transfer Objects (DTOs).

Contratos de datos entre capas.
Separan la estructura de entrada/salida de las entidades de dominio.
"""

from app.application.dto.lead_dto import (
    CreateLeadRequest,
    LeadResponse,
)
from app.application.dto.tracking_dto import (
    TrackEventRequest,
    TrackEventResponse,
    TrackingContext,
)
from app.application.dto.visitor_dto import (
    CreateVisitorRequest,
    VisitorResponse,
)

__all__ = [
    "CreateLeadRequest",
    "CreateVisitorRequest",
    "LeadResponse",
    "TrackEventRequest",
    "TrackEventResponse",
    "TrackingContext",
    "VisitorResponse",
]
