"""
📊 Tracking DTOs.

Contratos para requests/responses de tracking.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TrackingContext(BaseModel):
    """
    Contexto de tracking (datos técnicos del request).
    
    Se extrae del request HTTP pero no es parte del negocio.
    """
    ip_address: str = Field(..., description="IP del cliente")
    user_agent: str = Field(default="", description="User-Agent")
    country: Optional[str] = Field(default=None, description="País (Cloudflare)")
    city: Optional[str] = Field(default=None, description="Ciudad (Cloudflare)")
    region: Optional[str] = Field(default=None, description="Región (Cloudflare)")
    
    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Sanitiza IP."""
        # Limitar longitud
        return v[:45] if v else "unknown"  # IPv6 max length
    
    @field_validator("user_agent")
    @classmethod
    def validate_ua(cls, v: str) -> str:
        """Limita tamaño de User-Agent."""
        return v[:500] if v else ""


class TrackEventRequest(BaseModel):
    """
    Request para trackear evento.
    
    Validaciones Pydantic aseguran datos correctos antes de entrar al dominio.
    """
    event_name: str = Field(..., description="Nombre del evento")
    external_id: str = Field(..., description="ID del visitante", min_length=8, max_length=64)
    source_url: str = Field(..., description="URL donde ocurrió el evento")
    
    # Facebook tracking
    fbclid: Optional[str] = Field(default=None, description="Facebook Click ID")
    fbp: Optional[str] = Field(default=None, description="Facebook Browser ID")
    
    # Datos personalizados
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Datos adicionales")
    
    # UTM params
    utm_source: Optional[str] = Field(default=None)
    utm_medium: Optional[str] = Field(default=None)
    utm_campaign: Optional[str] = Field(default=None)
    utm_term: Optional[str] = Field(default=None)
    utm_content: Optional[str] = Field(default=None)
    
    # Seguridad
    turnstile_token: Optional[str] = Field(default=None, description="Cloudflare Turnstile token")
    
    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        """Normaliza nombre de evento."""
        return v.strip()
    
    @field_validator("source_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Valida URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v[:2048]  # Limitar longitud
    
    @field_validator("fbclid")
    @classmethod
    def validate_fbclid(cls, v: Optional[str]) -> Optional[str]:
        """Sanitiza fbclid."""
        if v:
            # Solo alphanumeric y algunos caracteres
            import re
            v = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        return v[:100] if v else None


class TrackEventResponse(BaseModel):
    """Response después de trackear evento."""
    success: bool
    event_id: Optional[str] = None
    status: str = Field(default="queued", description="queued|duplicate|error")
    message: Optional[str] = None
    
    @classmethod
    def ok(cls, event_id: str, message: str = "Event tracked") -> TrackEventResponse:
        return cls(success=True, event_id=event_id, status="queued", message=message)
    
    @classmethod
    def duplicate(cls, event_id: str) -> TrackEventResponse:
        return cls(success=True, event_id=event_id, status="duplicate", message="Event already processed")
    
    @classmethod
    def error(cls, message: str) -> TrackEventResponse:
        return cls(success=False, status="error", message=message)


class EventSummaryResponse(BaseModel):
    """Resumen de eventos para dashboards."""
    event_id: str
    event_name: str
    external_id: str
    timestamp: datetime
    source_url: str
    
    class Config:
        from_attributes = True
