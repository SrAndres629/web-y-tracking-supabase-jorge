"""
🎯 Lead Entity - Potencial cliente.

Un Lead representa una persona que ha mostrado interés
en los servicios (click WhatsApp, formulario, etc).

Relación con Visitor:
- Un Visitor puede convertirse en Lead
- Un Lead tiene un Visitor asociado (opcional)
- Lead tiene más datos de contacto (teléfono, email)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

try:
    from typing import TYPE_CHECKING, Any, Optional

    if TYPE_CHECKING:
        from typing import Self
    else:
        try:
            from typing import Self
        except ImportError:
            from typing_extensions import Self
except ImportError:
    from typing import Any, Optional

    from typing_extensions import Self

from enum import Enum

try:
    from app.domain.models.values import Email, ExternalId, Phone
except ImportError:
    # Reliable fallback for module-level types
    from typing import TypeAlias

    ExternalId: TypeAlias = str
    Phone: TypeAlias = str
    Email: TypeAlias = str


class LeadStatus(Enum):
    """
    Estados del lead en el funnel de ventas.

    Transiciones permitidas:
    NEW -> INTERESTED -> NURTURING -> BOOKED -> CLIENT_ACTIVE -> CLIENT_LOYAL
    NEW -> GHOST -> ARCHIVED
    """

    NEW = "new"  # Recién capturado
    INTERESTED = "interested"  # Mostró interés inicial
    NURTURING = "nurturing"  # En seguimiento activo
    GHOST = "ghost"  # No responde
    BOOKED = "booked"  # Agendó cita
    CLIENT_ACTIVE = "client_active"  # Cliente actual (tratamiento)
    CLIENT_LOYAL = "client_loyal"  # Cliente recurrente
    ARCHIVED = "archived"  # Descartado/archivado


@dataclass
class Lead:
    """
    Entidad: Potencial cliente.

    Identity: internal ID (UUID) o phone (único)

    Attributes:
        id: UUID único del lead
        external_id: Referencia al Visitor (opcional)
        phone: Teléfono principal (WhatsApp)
        email: Email opcional
        name: Nombre del lead
        status: Estado en el funnel
        fbclid: Click ID para atribución
        meta_lead_id: ID de lead en Meta (si viene de Lead Ads)
        score: Puntuación 0-100 (lead scoring)
        pain_point: Dolor/problemática principal
        service_interest: Servicio de interés
        created_at: Fecha de creación
        updated_at: Última actualización
    """

    # Identity
    id: str  # UUID

    # Contact (required)
    phone: Phone

    # Optional contact
    email: Optional[Email] = None
    name: Optional[str] = None

    # Link to visitor
    external_id: Optional[ExternalId] = None

    # Attribution
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    meta_lead_id: Optional[str] = None

    # State
    status: LeadStatus = field(default_factory=lambda: LeadStatus.NEW)
    score: int = field(default=50)  # 0-100

    # Qualification
    pain_point: Optional[str] = None
    service_interest: Optional[str] = None
    utm_source: Optional[str] = None
    utm_campaign: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Tracking flags
    sent_to_meta: bool = False  # Evento Lead enviado a Meta CAPI

    @classmethod
    def create(
        cls,
        phone: Phone,
        name: Optional[str] = None,
        email: Optional[Email] = None,
        external_id: Optional[ExternalId] = None,
        fbclid: Optional[str] = None,
        service_interest: Optional[str] = None,
    ) -> Self:
        """
        Factory method para crear nuevo lead.

        Genera UUID automáticamente.
        """
        import uuid

        # Sanitize name
        if name:
            name = str(name).strip()[:100] or None

        return cls(
            id=str(uuid.uuid4()),
            phone=phone,
            email=email,
            name=name,
            external_id=external_id,
            fbclid=fbclid,
            service_interest=service_interest,
        )

    def update_status(self, new_status: LeadStatus) -> None:
        """
        Actualiza estado del lead.

        Registra timestamp de actualización.
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()

        # Score adjustments based on status
        if new_status == LeadStatus.BOOKED:
            self.score = min(100, self.score + 20)
        elif new_status == LeadStatus.CLIENT_ACTIVE:
            self.score = 100
        elif new_status == LeadStatus.GHOST:
            self.score = max(0, self.score - 10)

    def update_contact_info(
        self,
        name: Optional[str] = None,
        email: Optional[Email] = None,
    ) -> None:
        """Actualiza información de contacto."""
        if name:
            self.name = str(name).strip()[:100] or self.name
        if email:
            self.email = email
        self.updated_at = datetime.utcnow()

    def qualify(
        self,
        pain_point: Optional[str] = None,
        service_interest: Optional[str] = None,
    ) -> None:
        """Califica el lead con más información."""
        if pain_point:
            self.pain_point = str(pain_point)[:200]
        if service_interest:
            self.service_interest = str(service_interest)[:100]
        self.updated_at = datetime.utcnow()

    def mark_as_sent_to_meta(self) -> None:
        """Marca que el evento Lead fue enviado a Meta CAPI."""
        self.sent_to_meta = True
        self.updated_at = datetime.utcnow()

    @property
    def is_qualified(self) -> bool:
        """True si tiene suficiente información para contacto."""
        return bool(self.name and (self.email or self.phone))

    @property
    def is_hot(self) -> bool:
        """True si es lead prioritario (alto score + activo)."""
        return self.score >= 70 and self.status in [
            LeadStatus.NEW,
            LeadStatus.INTERESTED,
            LeadStatus.NURTURING,
        ]

    def to_meta_custom_data(self) -> dict[str, Any]:
        """Datos personalizados para Meta CAPI."""
        return {
            "content_name": self.service_interest or "Consultation",
            "content_category": "lead",
            "lead_source": self.utm_source or "website",
            "value": self.score,
            "currency": "BOB",
        }

    def __repr__(self) -> str:
        return f"Lead({str(self.id)[:8]}, {self.phone}, {self.status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lead):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
