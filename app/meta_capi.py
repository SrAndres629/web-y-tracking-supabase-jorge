"""
📘 META CAPI BRIDGE (Atomic Architecture compatibility)
Restores legacy app.meta_capi functions and classes during refactoring.
"""
import logging
import time
from typing import Optional, Dict, Any
from app.tracking import send_event_async

logger = logging.getLogger(__name__)

# Constants for tests/legacy code
SDK_AVAILABLE = False

class MetaEventType:
    PURCHASE = "Purchase"
    LEAD = "Lead"
    CONTACT = "Contact"
    VIEW_CONTENT = "ViewContent"

class EnhancedUserData:
    """Legacy class used in tests and command handlers."""
    def __init__(self, email=None, phone=None, city=None, country=None, **kwargs):
        self.email = email
        self.phone = phone
        self.city = city
        self.country = country
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.external_id = kwargs.get("external_id")

    def to_sdk_user_data(self):
        # Mock for tests that expect an SDK-like object
        class MockUD:
            def __init__(self):
                self.email = None
                self.phone = None
                self.city = None
                self.country_code = None
        
        ud = MockUD()
        if self.email: ud.email = self.email.lower().strip()
        if self.phone: ud.phone = "".join(filter(str.isdigit, self.phone))
        if self.city: ud.city = self.city.lower().replace(" ", "")
        if self.country: ud.country_code = self.country.lower()
        return ud

class EnhancedCustomData:
    """Legacy class used in tests."""
    def __init__(self, **kwargs):
        self.data = kwargs

async def send_elite_event(**kwargs):
    """
    Main bridge function for routers and commands.
    Satisfies: from app.meta_capi import send_elite_event
    """
    try:
        # Convert some argument names if necessary (e.g., url -> event_source_url)
        params = kwargs.copy()
        if "url" in params and "event_source_url" not in params:
            params["event_source_url"] = params.pop("url")
            
        success = await send_event_async(**params)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        logger.error(f"Bridge send_elite_event error: {e}")
        return {"status": "error", "message": str(e)}

class EliteMetaCAPIService:
    """Legacy service class expected by unit tests."""
    def __init__(self):
        self.sandbox_mode = False
        self._deduplicate_internal = lambda x: True

    def _deduplicate(self, event_id):
        return self._deduplicate_internal(event_id)

    async def send_event(self, **kwargs):
        if self.sandbox_mode:
            return {"status": "sandbox"}
        
        event_id = kwargs.get("event_id")
        if event_id and not self._deduplicate(event_id):
            return {"status": "duplicate", "event_id": event_id}
            
        return await send_elite_event(**kwargs)

# For tests that patch UserData
class UserData:
    pass
