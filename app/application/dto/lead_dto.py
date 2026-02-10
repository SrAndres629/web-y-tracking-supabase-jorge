"""
🎯 Lead DTOs.
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CreateLeadRequest(BaseModel):
    """Request para crear lead."""
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono (WhatsApp)")
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=254)
    external_id: Optional[str] = Field(default=None, description="ID del visitante asociado")
    fbclid: Optional[str] = Field(default=None)
    service_interest: Optional[str] = Field(default=None, max_length=100)
    
    # UTM
    utm_source: Optional[str] = None
    utm_campaign: Optional[str] = None
    
    @field_validator("phone")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        """Extrae solo dígitos y +."""
        return ''.join(c for c in v if c.isdigit() or c == '+')
    
    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Limpia nombre."""
        if v:
            v = v.strip()
            return v if v else None
        return None


class LeadResponse(BaseModel):
    """Response con datos de lead."""
    id: str
    phone: str
    name: Optional[str]
    email: Optional[str]
    status: str
    score: int
    service_interest: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateLeadStatusRequest(BaseModel):
    """Request para actualizar estado de lead."""
    status: str = Field(..., pattern="^(new|interested|nurturing|ghost|booked|client_active|client_loyal|archived)$")
