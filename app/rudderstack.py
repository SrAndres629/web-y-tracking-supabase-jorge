# =================================================================
# RUDDERSTACK.PY - CDP Integration Service
# Jorge Aguirre Flores Web
# =================================================================

import logging
import rudderstack.analytics as analytics
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RudderStackService:
    """
    Service to send events to RudderStack CDP.
    Acts as a 'Brain' triggering destinations like GA4, Mixpanel, etc.
    """
    
    def __init__(self):
        self.enabled = False
        if settings.rudderstack_enabled:
            try:
                analytics.write_key = settings.RUDDERSTACK_WRITE_KEY
                analytics.data_plane_url = settings.RUDDERSTACK_DATA_PLANE_URL
                # Disable gzip to avoid compatibility issues on some environments
                analytics.gzip = False 
                self.enabled = True
                logger.info("✅ RudderStack initialized")
            except Exception as e:
                logger.error(f"❌ RudderStack init failed: {e}")
                self.enabled = False
        else:
            logger.debug("ℹ️ RudderStack disabled (config missing)")

    def identify(self, user_id: str, traits: Optional[Dict[str, Any]] = None):
        """Identify a user (link unknown visitor to known user)"""
        if not self.enabled:
            return

        try:
            analytics.identify(user_id, traits or {})
            logger.debug(f"👤 [RudderStack] Identified: {user_id}")
        except Exception as e:
            logger.error(f"❌ [RudderStack] Identify error: {e}")

    def track(
        self, 
        user_id: str, 
        event_name: str, 
        properties: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Track an event"""
        if not self.enabled:
            return

        try:
            analytics.track(
                user_id=user_id,
                event=event_name,
                properties=properties or {},
                context=context or {}
            )
            logger.info(f"✅ [RudderStack] Event sent: {event_name}")
        except Exception as e:
            logger.error(f"❌ [RudderStack] Track error: {e}")

# Singleton Instance
rudder_service = RudderStackService()
