"""
👤 Visitor DTOs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateVisitorRequest(BaseModel):
    """Request para crear visitante."""

    ip_address: str
    user_agent: str
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    source: str = Field(default="pageview")

    # UTM
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class VisitorResponse(BaseModel):
    """Response con datos de visitante."""

    external_id: str
    fbclid: Optional[str]
    fbp: Optional[str]
    source: str
    visit_count: int
    created_at: datetime
    last_seen: datetime
    model_config = ConfigDict(from_attributes=True)


class VisitorListResponse(BaseModel):
    """Lista paginada de visitantes."""

    items: list[VisitorResponse]
    total: int
    limit: int
    offset: int
