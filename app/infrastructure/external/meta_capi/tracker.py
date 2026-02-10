"""
📘 Meta CAPI Tracker Implementation.

Envía eventos a Meta Conversions API.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from app.application.interfaces.tracker_port import TrackerPort
from app.domain.models.events import TrackingEvent
from app.domain.models.visitor import Visitor
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class MetaTracker(TrackerPort):
    """
    Tracker para Meta Conversions API.
    
    Usa HTTP API directo (no SDK) para menor overhead.
    """
    
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self._settings = get_settings()
        self._client = http_client
        self._enabled = self._settings.meta.is_configured and not self._settings.meta.sandbox_mode
    
    @property
    def name(self) -> str:
        return "meta_capi"
    
    @property
    def _http_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def track(self, event: TrackingEvent, visitor: Visitor) -> bool:
        """
        Envia evento a Meta CAPI.
        
        Construye payload según especificación de Meta.
        """
        if not self._enabled:
            if self._settings.meta.sandbox_mode:
                logger.info(f"🛡️ [SANDBOX] Meta CAPI: {event.event_name.value}")
            else:
                logger.debug("Meta CAPI not configured, skipping")
            return True
        
        try:
            payload = self._build_payload(event, visitor)
            
            response = await self._http_client.post(
                self._settings.meta.api_url,
                json=payload,
                params={"access_token": self._settings.meta.access_token},
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Meta CAPI: {event.event_name.value} sent")
                return True
            else:
                logger.warning(f"⚠️ Meta CAPI failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Meta CAPI error: {e}")
            return False
    
    def _build_payload(self, event: TrackingEvent, visitor: Visitor) -> dict:
        """Construye payload para Meta CAPI."""
        from app.core.validators import hash_sha256
        
        # User Data (hashed)
        user_data = {
            "external_id": hash_sha256(visitor.external_id.value),
        }
        
        if visitor.fbclid:
            user_data["fbc"] = f"fb.1.{int(time.time())}.{visitor.fbclid}"
        
        if visitor.fbp:
            user_data["fbp"] = visitor.fbp
        
        if visitor.ip_address:
            user_data["client_ip_address"] = visitor.ip_address
        
        if visitor.user_agent:
            user_data["client_user_agent"] = visitor.user_agent
        
        # Geo data (hashed)
        if visitor.geo.country:
            user_data["country"] = hash_sha256(visitor.geo.country.lower())
        
        # Event Data
        event_data = {
            "event_name": event.event_name.value,
            "event_time": int(event.timestamp.timestamp()),
            "event_id": event.event_id.value,
            "event_source_url": event.source_url,
            "action_source": "website",
            "user_data": user_data,
        }
        
        # Custom Data
        if event.custom_data:
            event_data["custom_data"] = event.custom_data
        
        # Test Event Code (development)
        payload = {"data": [event_data]}
        if self._settings.meta.test_event_code:
            payload["test_event_code"] = self._settings.meta.test_event_code
        
        return payload
    
    async def health_check(self) -> bool:
        """Verifica conectividad con Meta."""
        if not self._enabled:
            return False
        
        try:
            response = await self._http_client.get(
                "https://graph.facebook.com/v21.0/me",
                params={"access_token": self._settings.meta.access_token},
            )
            return response.status_code == 200
        except:
            return False
