"""
📊 RudderStack Tracker Implementation.

Envía eventos a RudderStack (CDP).
"""

from __future__ import annotations

import logging
from typing import Optional

from app.application.interfaces.tracker_port import TrackerPort
from app.domain.models.events import TrackingEvent
from app.domain.models.visitor import Visitor
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class RudderStackTracker(TrackerPort):
    """
    Tracker para RudderStack.
    
    RudderStack es un Customer Data Platform (CDP)
    que centraliza eventos para múltiples destinos.
    """
    
    def __init__(self):
        self._settings = get_settings()
        self._enabled = bool(
            self._settings.external.rudderstack_write_key and
            self._settings.external.rudderstack_data_plane_url
        )
        self._client = None
    
    @property
    def name(self) -> str:
        return "rudderstack"
    
    def _get_client(self):
        """Lazy init del cliente RudderStack."""
        if self._client is None and self._enabled:
            try:
                from rudder_sdk_python import RudderAnalytics
                self._client = RudderAnalytics(
                    write_key=self._settings.external.rudderstack_write_key,
                    data_plane_url=self._settings.external.rudderstack_data_plane_url,
                )
            except Exception as e:
                logger.error(f"Failed to init RudderStack: {e}")
                self._enabled = False
        return self._client
    
    async def track(self, event: TrackingEvent, visitor: Visitor) -> bool:
        """Envia evento a RudderStack."""
        if not self._enabled:
            logger.debug("RudderStack not configured, skipping")
            return True
        
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Usar external_id como user_id
            user_id = visitor.external_id.value
            
            # Track event
            client.track(
                user_id=user_id,
                event=event.event_name.value,
                properties={
                    "event_id": event.event_id.value,
                    "source_url": event.source_url,
                    **event.custom_data,
                },
                context={
                    "traits": {
                        "fbclid": visitor.fbclid,
                        "fbp": visitor.fbp,
                    },
                    "ip": visitor.ip_address,
                    "userAgent": visitor.user_agent,
                }
            )
            
            logger.debug(f"✅ RudderStack: {event.event_name.value} sent")
            return True
            
        except Exception as e:
            logger.error(f"❌ RudderStack error: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Verifica conectividad."""
        return self._enabled and self._get_client() is not None
