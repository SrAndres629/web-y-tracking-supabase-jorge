"""
📋 Data Transfer Objects (DTOs).

Contratos de datos entre capas.
Separan la estructura de entrada/salida de las entidades de dominio.
"""

from app.application.dto.tracking_dto import (
    TrackEventRequest,
    TrackEventResponse,
    TrackingContext,
)
from app.application.dto.visitor_dto import (
    VisitorResponse,
    CreateVisitorRequest,
)
from app.application.dto.lead_dto import (
    CreateLeadRequest,
    LeadResponse,
)

__all__ = [
    "TrackEventRequest",
    "TrackEventResponse",
    "TrackingContext",
    "VisitorResponse",
    "CreateVisitorRequest",
    "CreateLeadRequest",
    "LeadResponse",
]
