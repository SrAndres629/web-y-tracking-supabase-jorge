# =================================================================
# MODELS.PY - Pydantic Schemas para validación de requests
# Jorge Aguirre Flores Web
# =================================================================
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    INTERESTED = "INTERESTED"
    GHOST = "GHOST"
    BOOKED = "BOOKED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"



class LeadTrackRequest(BaseModel):
    """Schema para POST /track-lead"""
    event_id: str = Field(..., description="ID único del evento para deduplicación")
    source: str = Field(..., description="Fuente del lead (ej: 'Hero CTA')")
    service_data: Optional[dict] = Field(default=None, description="Datos granulares: nombre, id, intención")
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class ViewContentRequest(BaseModel):
    """Schema para POST /track-viewcontent"""
    service: str = Field(..., description="Nombre del servicio visto")
    category: str = Field(..., description="Categoría del servicio")
    price: Optional[float] = Field(default=0, description="Precio del servicio en USD")
    event_id: Optional[str] = Field(default=None, description="ID generado en frontend para deduplicación")


class SliderTrackRequest(BaseModel):
    """Schema para POST /track-slider"""
    event_id: str = Field(..., description="ID único del evento")
    service_name: str = Field(..., description="Nombre del servicio (ej: 'Microblading 3D')")
    service_id: str = Field(..., description="ID técnico del servicio")
    interaction_type: str = Field(default="compare_before_after", description="Tipo de interacción")


class VisitorResponse(BaseModel):
    """Response schema para visitantes"""
    id: int
    external_id: str
    fbclid: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class Visitor(BaseModel):
    """Pydantic model representativo de la tabla visitors"""
    id: Optional[int] = None
    external_id: str
    fbclid: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: Optional[str] = "pageview"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    timestamp: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema para /health"""
    status: str
    database: str
    timestamp: str
    service: str


class TrackResponse(BaseModel):
    """Response genérico para endpoints de tracking"""
    status: str
    event_id: Optional[str] = None
    category: Optional[str] = None


class ConfirmSaleResponse(BaseModel):
    """Response para POST /admin/confirm/{visitor_id}"""
    status: str
    visitor_id: int
    value: float
    event_id: str



class LeadCreate(BaseModel):
    """Schema para crear/actualizar un Lead"""
    whatsapp_phone: str
    meta_lead_id: Optional[str] = None
    click_id: Optional[str] = None  # fbclid
    email: Optional[str] = None
    name: Optional[str] = None
    extra_data: Optional[dict] = None

class InteractionCreate(BaseModel):
    """Schema para registrar una interacción"""
    lead_id: str
    role: str = Field(..., description="'user', 'assistant', 'system'")
    content: str
    
class ErrorResponse(BaseModel):
    """Response para errores"""
    status: str = "error"
    error: str
