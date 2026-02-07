# =================================================================
# META_CAPI.PY - Elite Meta Conversions API Service
# Using Official facebook-business SDK
# Jorge Aguirre Flores Web
# =================================================================
# 
# ARCHITECTURE: Professional-grade CAPI implementation
# - Uses official Meta SDK for guaranteed compatibility
# - Automatic SHA256 hashing compliance
# - Built-in retry and error handling
# - Prepared for Advanced Matching (fn, ln, ct, zp)
# 
# MIGRATION: This replaces manual HTTP requests in tracking.py
# =================================================================

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from app.config import settings
from app.retry_queue import add_to_retry_queue

logger = logging.getLogger(__name__)

# =================================================================
# SDK INITIALIZATION
# =================================================================

SDK_AVAILABLE = False
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.serverside.event import Event
    from facebook_business.adobjects.serverside.event_request import EventRequest
    from facebook_business.adobjects.serverside.user_data import UserData
    from facebook_business.adobjects.serverside.custom_data import CustomData
    from facebook_business.adobjects.serverside.action_source import ActionSource
    from facebook_business.adobjects.serverside.content import Content
    
    # Initialize API if credentials are available
    if settings.META_ACCESS_TOKEN and settings.META_PIXEL_ID:
        FacebookAdsApi.init(access_token=settings.META_ACCESS_TOKEN)
        SDK_AVAILABLE = True
        logger.info("✅ Meta Business SDK initialized")
    else:
        logger.warning("⚠️ Meta credentials missing - SDK not initialized")
        
except ImportError as e:
    logger.warning(f"⚠️ facebook-business SDK not installed: {e}")
except Exception as e:
    logger.error(f"❌ Meta SDK initialization failed: {e}")


# =================================================================
# EVENT TYPES (Standard Meta Events)
# =================================================================

class MetaEventType(Enum):
    """Standard Meta Pixel Events with descriptions"""
    PAGE_VIEW = "PageView"
    VIEW_CONTENT = "ViewContent"
    LEAD = "Lead"
    CONTACT = "Contact"
    INITIATE_CHECKOUT = "InitiateCheckout"
    PURCHASE = "Purchase"
    COMPLETE_REGISTRATION = "CompleteRegistration"
    SCHEDULE = "Schedule"
    CUSTOMIZE_PRODUCT = "CustomizeProduct"  # Used for engagement tracking


# =================================================================
# USER DATA BUILDER (Advanced Matching)
# =================================================================

@dataclass
class EnhancedUserData:
    """
    Enhanced User Data for Meta CAPI with Advanced Matching.
    All PII is automatically hashed by the SDK.
    """
    # Core identifiers (High EMQ impact)
    client_ip_address: Optional[str] = None
    client_user_agent: Optional[str] = None
    external_id: Optional[str] = None
    
    # Facebook identifiers (Highest EMQ impact)
    fbc: Optional[str] = None  # Click ID cookie
    fbp: Optional[str] = None  # Browser ID cookie
    fb_login_id: Optional[str] = None  # If user logged in via FB
    
    # Contact info (High EMQ impact)
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Personal info (Medium EMQ impact) - Prepared for future capture
    first_name: Optional[str] = None  # fn
    last_name: Optional[str] = None   # ln
    
    # Location data (Medium EMQ impact)
    city: Optional[str] = None        # ct
    state: Optional[str] = None       # st
    zip_code: Optional[str] = None    # zp
    country: Optional[str] = "bo"     # Default to Bolivia
    
    # Gender & DOB (Low EMQ impact)
    gender: Optional[str] = None      # m or f
    date_of_birth: Optional[str] = None  # YYYYMMDD
    
    def to_sdk_user_data(self) -> "UserData":
        """Convert to SDK UserData object with automatic hashing"""
        if not SDK_AVAILABLE:
            raise RuntimeError("Meta SDK not available")
        
        user_data = UserData()
        self._set_basic_identifiers(user_data)
        self._set_fb_identifiers(user_data)
        self._set_contact_info(user_data)
        self._set_personal_info(user_data)
        self._set_location_info(user_data)
        self._set_demographics(user_data)
        return user_data

    def _set_basic_identifiers(self, user_data: "UserData"):
        if self.client_ip_address:
            user_data.client_ip_address = self.client_ip_address
        if self.client_user_agent:
            user_data.client_user_agent = self.client_user_agent
        if self.external_id:
            user_data.external_id = self.external_id

    def _set_fb_identifiers(self, user_data: "UserData"):
        if self.fbc:
            user_data.fbc = self.fbc
        if self.fbp:
            user_data.fbp = self.fbp
        if self.fb_login_id:
            user_data.fb_login_id = self.fb_login_id

    def _set_contact_info(self, user_data: "UserData"):
        if self.email:
            user_data.email = self.email.lower().strip()
        if self.phone:
            phone_clean = "".join(filter(str.isdigit, self.phone))
            if not phone_clean.startswith("591"):
                phone_clean = "591" + phone_clean
            user_data.phone = phone_clean

    def _set_personal_info(self, user_data: "UserData"):
        if self.first_name:
            user_data.first_name = self.first_name.lower().strip()
        if self.last_name:
            user_data.last_name = self.last_name.lower().strip()

    def _set_location_info(self, user_data: "UserData"):
        if self.city:
            user_data.city = self.city.lower().replace(" ", "")
        if self.state:
            user_data.state = self.state.lower().replace(" ", "")
        if self.zip_code:
            user_data.zip_code = self.zip_code
        if self.country:
            user_data.country_code = self.country.lower()

    def _set_demographics(self, user_data: "UserData"):
        if self.gender:
            user_data.gender = self.gender.lower()[0] if self.gender else None
        if self.date_of_birth:
            user_data.date_of_birth = self.date_of_birth


# =================================================================
# CUSTOM DATA BUILDER
# =================================================================

@dataclass  
class EnhancedCustomData:
    """Custom data for Meta events"""
    content_name: Optional[str] = None
    content_category: Optional[str] = None
    content_type: Optional[str] = "product"
    content_ids: List[str] = field(default_factory=list)
    value: Optional[float] = None
    currency: str = "BOB"  # Bolivian Boliviano
    
    # Custom fields
    lead_source: Optional[str] = None
    engagement_level: Optional[str] = None
    scroll_depth: Optional[int] = None
    time_on_page: Optional[int] = None
    
    def to_sdk_custom_data(self) -> "CustomData":
        """Convert to SDK CustomData object"""
        if not SDK_AVAILABLE:
            raise RuntimeError("Meta SDK not available")
            
        custom_data = CustomData()
        
        if self.content_name:
            custom_data.content_name = self.content_name
        if self.content_category:
            custom_data.content_category = self.content_category
        if self.content_type:
            custom_data.content_type = self.content_type
        if self.content_ids:
            custom_data.content_ids = self.content_ids
        if self.value:
            custom_data.value = self.value
        if self.currency:
            custom_data.currency = self.currency
            
        return custom_data


# =================================================================
# ELITE CAPI SERVICE
# =================================================================

class EliteMetaCAPIService:
    """
    Elite-grade Meta Conversions API Service.
    Uses official SDK with Redis deduplication.
    """
    
    def __init__(self):
        self.pixel_id = settings.META_PIXEL_ID
        self.test_event_code = settings.TEST_EVENT_CODE
        self.sandbox_mode = settings.META_SANDBOX_MODE
        
        # Import cache functions
        try:
            from app.cache import deduplicate_event
            self._deduplicate = deduplicate_event
            self._cache_enabled = True
        except ImportError:
            self._deduplicate = lambda x, y: True  # Always allow if no cache
            self._cache_enabled = False
    
    def send_event(
        self,
        event_name: str,
        event_id: str,
        event_source_url: str,
        user_data: EnhancedUserData,
        custom_data: Optional[EnhancedCustomData] = None,
        event_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send event to Meta CAPI using official SDK."""
        # 1. Guards
        if self.sandbox_mode:
            logger.info(f"🛡️ [SANDBOX] {event_name} intercepted")
            return {"status": "sandbox", "event_id": event_id}
        
        if not self._deduplicate(event_id, event_name):
            logger.info(f"🔄 [DEDUP] Skipped duplicate {event_name}: {event_id[:16]}...")
            return {"status": "duplicate", "event_id": event_id}
        
        if not SDK_AVAILABLE:
            return self._fallback_http_send(event_name, event_id, event_source_url, user_data, custom_data)
        
        # 2. Build & Execute
        try:
            request = self._build_event_request(event_name, event_id, event_source_url, user_data, custom_data, event_time)
            response = request.execute()
            
            logger.info(f"✅ [META CAPI SDK] {event_name} sent successfully")
            return {
                "status": "success", "event_id": event_id,
                "events_received": response.get("events_received", 1),
                "fbtrace_id": response.get("fbtrace_id")
            }
        except Exception as e:
            return self._handle_capi_error(e, event_name, event_id, event_source_url, user_data, custom_data)

    def _build_event_request(self, event_name, event_id, url, user_data, custom_data, event_time):
        event = Event(
            event_name=event_name,
            event_time=event_time or int(time.time()),
            event_id=event_id,
            event_source_url=url,
            action_source=ActionSource.WEBSITE,
            user_data=user_data.to_sdk_user_data()
        )
        if custom_data:
            event.custom_data = custom_data.to_sdk_custom_data()
        
        request = EventRequest(pixel_id=self.pixel_id, events=[event])
        if self.test_event_code:
            request.test_event_code = self.test_event_code
        return request

    def _handle_capi_error(self, e, name, event_id, url, user_data, custom_data):
        logger.error(f"❌ [META CAPI SDK] Error: {e}")
        add_to_retry_queue(name, {
            "url": url, "user_data": vars(user_data),
            "custom_data": vars(custom_data) if custom_data else None,
            "event_id": event_id
        })
        return {"status": "queued", "event_id": event_id, "error": str(e)}
    
    def _fallback_http_send(
        self,
        event_name: str,
        event_id: str,
        event_source_url: str,
        user_data: EnhancedUserData,
        custom_data: Optional[EnhancedCustomData]
    ) -> Dict[str, Any]:
        """Fallback to manual HTTP if SDK unavailable"""
        try:
            from app.tracking import send_event
            
            # Convert to legacy format
            fbclid = None
            if user_data.fbc and "." in user_data.fbc:
                parts = user_data.fbc.split(".")
                if len(parts) >= 4:
                    fbclid = parts[3]
            
            success = send_event(
                event_name=event_name,
                event_source_url=event_source_url,
                client_ip=user_data.client_ip_address or "",
                user_agent=user_data.client_user_agent or "",
                event_id=event_id,
                fbclid=fbclid,
                fbp=user_data.fbp,
                external_id=user_data.external_id,
                phone=user_data.phone,
                email=user_data.email
            )
            
            return {
                "status": "success" if success else "error",
                "event_id": event_id,
                "method": "http_fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ [FALLBACK] Error: {e}")
            return {"status": "error", "event_id": event_id, "error": str(e)}
    
    # =================================================================
    # CONVENIENCE METHODS (Pre-built for common events)
    # =================================================================
    
    def track_page_view(
        self,
        event_id: str,
        url: str,
        user_data: EnhancedUserData
    ) -> Dict[str, Any]:
        """Track PageView event"""
        return self.send_event(
            event_name=MetaEventType.PAGE_VIEW.value,
            event_id=event_id,
            event_source_url=url,
            user_data=user_data
        )
    
    def track_lead(
        self,
        event_id: str,
        url: str,
        user_data: EnhancedUserData,
        lead_source: str = "website",
        service_interest: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track Lead event (WhatsApp click, form submit)"""
        custom_data = EnhancedCustomData(
            content_name=service_interest or lead_source,
            content_category="lead",
            lead_source=lead_source
        )
        
        return self.send_event(
            event_name=MetaEventType.LEAD.value,
            event_id=event_id,
            event_source_url=url,
            user_data=user_data,
            custom_data=custom_data
        )
    
    def track_view_content(
        self,
        event_id: str,
        url: str,
        user_data: EnhancedUserData,
        content_name: str,
        content_category: str = "service"
    ) -> Dict[str, Any]:
        """Track ViewContent event (service view)"""
        custom_data = EnhancedCustomData(
            content_name=content_name,
            content_category=content_category
        )
        
        return self.send_event(
            event_name=MetaEventType.VIEW_CONTENT.value,
            event_id=event_id,
            event_source_url=url,
            user_data=user_data,
            custom_data=custom_data
        )
    
    def track_contact(
        self,
        event_id: str,
        url: str,
        user_data: EnhancedUserData,
        contact_method: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Track Contact event (pre-WhatsApp click)"""
        custom_data = EnhancedCustomData(
            content_name=contact_method,
            content_category="consultation_request"
        )
        
        return self.send_event(
            event_name=MetaEventType.CONTACT.value,
            event_id=event_id,
            event_source_url=url,
            user_data=user_data,
            custom_data=custom_data
        )


# =================================================================
# SINGLETON INSTANCE
# =================================================================

elite_capi = EliteMetaCAPIService()


# =================================================================
# QUICK ACCESS FUNCTIONS (For backward compatibility)
# =================================================================

def send_elite_event(
    event_name: str, event_id: str, url: str, client_ip: str, user_agent: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to send events with minimal boilerplate.
    Compatible with existing code structure.
    """
    user_data = EnhancedUserData(
        client_ip_address=client_ip,
        client_user_agent=user_agent,
        external_id=kwargs.get("external_id"),
        fbc=kwargs.get("fbc"),
        fbp=kwargs.get("fbp"),
        phone=kwargs.get("phone"),
        email=kwargs.get("email"),
        first_name=kwargs.get("first_name"),
        last_name=kwargs.get("last_name"),
        city=kwargs.get("city"),
        state=kwargs.get("state"),
        zip_code=kwargs.get("zip_code"),
        country=kwargs.get("country", "bo")
    )
    
    custom_data = kwargs.get("custom_data")
    enhanced_custom = None
    if custom_data:
        enhanced_custom = EnhancedCustomData(
            content_name=custom_data.get("content_name"),
            content_category=custom_data.get("content_category"),
            lead_source=custom_data.get("lead_source")
        )
    
    return elite_capi.send_event(
        event_name=event_name, event_id=event_id, event_source_url=url,
        user_data=user_data, custom_data=enhanced_custom
    )
