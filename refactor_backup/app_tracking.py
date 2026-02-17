# =================================================================
# TRACKING.PY - Meta Conversions API (CAPI) - High Performance
# Jorge Aguirre Flores Web
# =================================================================
import hashlib
import logging
import os
import random
import string
import time
from typing import Any, Dict, Optional

import httpx

from app.config import settings

# 🚀 Redis Cache for Ultra-Fast Deduplication
try:
    from app.cache import cache_visitor_data, deduplicate_event, get_cached_visitor

    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False

    def deduplicate_event(event_id: str, event_name: str = "event") -> bool:
        """Mock deduplication: Always returns True (Success)"""
        return True

    def cache_visitor_data(external_id: str, data: Dict[str, Any], ttl_hours: int = 24) -> None:
        """Mock cache visitor data"""
        pass

    def get_cached_visitor(external_id: str) -> Optional[Dict[str, Any]]:
        """Mock get cached visitor"""
        return None


logger = logging.getLogger(__name__)

# =================================================================
# HTTP CLIENTS (SINGLETONS FOR PERSISTENT POOLING)
# =================================================================
# reusing clients enables HTTP/2 and avoids SSL Handshake overhead (save ~200ms)
timeout = httpx.Timeout(10.0, connect=5.0)
sync_client = httpx.Client(timeout=timeout, http2=True)

# Async client for FastAPI routes (future proofing)
# In audit/test runs, avoid creating a global async client to prevent
# unclosed event loop warnings during pytest teardown.
_AUDIT_MODE = os.getenv("AUDIT_MODE", "").strip() == "1"
async_client = None if _AUDIT_MODE else httpx.AsyncClient(timeout=timeout, http2=True)

# =================================================================
# HASHING FUNCTIONS
# =================================================================


def hash_data(value: str) -> Optional[str]:
    """Hash SHA256 for user data (Meta requirement)"""
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode("utf-8")).hexdigest()


def generate_external_id(ip: str, user_agent: str) -> str:
    """Generate deterministic ID based on IP + UA"""
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]


def generate_fbc(fbclid: str) -> Optional[str]:
    """Generate fbc parameter"""
    if not fbclid:
        return None
    timestamp = int(time.time())
    return f"fb.1.{timestamp}.{fbclid}"


def generate_fbp() -> str:
    """Generate fbp parameter (Browser Display ID)"""
    import random

    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    return f"fb.1.{timestamp}.{random_id}"


def generate_event_id(event_name: str) -> str:
    """Generate unique event ID (evt_timestamp_name)"""
    timestamp_ns = time.time_ns()
    # 🛡️ ENTROPY BOOST: Add 6 chars of randomness to ensure >100k collisions/sec resistance
    entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"evt_{timestamp_ns}_{entropy}"


def extract_fbclid_from_fbc(fbc_cookie: str) -> Optional[str]:
    """Extract fbclid from cookie"""
    if not fbc_cookie or not fbc_cookie.startswith("fb.1."):
        return None

    parts = fbc_cookie.split(".")
    if len(parts) >= 4:
        return parts[3]
    return None


def get_prioritized_fbclid(url_fbclid: Optional[str], cookie_fbc: Optional[str]) -> Optional[str]:
    """
    Decides which fbclid to use.
    Priority: 1. URL Parameter (Fresh click) -> 2. Cookie (Persistent session)
    """
    if url_fbclid:
        return url_fbclid

    if cookie_fbc:
        return extract_fbclid_from_fbc(cookie_fbc)

    return None


# =================================================================
# META CONVERSIONS API (CORE LOGIC)
# =================================================================


def _build_payload(  # noqa: C901
    event_name: str,
    event_source_url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    fbclid: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    # 🚀 NEW: Advanced Matching Enhancement
    country: Optional[str] = None,
    city: Optional[str] = None,
    fb_browser_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Constructs the JSON payload for Meta CAPI with Enhanced Matching"""

    # User Data (Advanced Matching)
    user_data = {
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }

    if external_id:
        user_data["external_id"] = hash_data(external_id)
    if fbclid:
        user_data["fbc"] = generate_fbc(fbclid)
    if fbp:
        user_data["fbp"] = fbp
    if fb_browser_id:
        user_data["fb_browser_id"] = fb_browser_id
    if phone:
        # Normalize phone: remove non-digits, ensure country code
        clean_phone = "".join(filter(str.isdigit, phone))
        if not clean_phone.startswith("591"):
            clean_phone = "591" + clean_phone  # Bolivia country code
        user_data["ph"] = hash_data(clean_phone)
    if email:
        user_data["em"] = hash_data(email)

    # 🌍 Geo Data (Improves match quality for local businesses)
    if country:
        user_data["country"] = hash_data(country.lower())
    else:
        user_data["country"] = hash_data("bo")  # Bolivia default

    if city:
        user_data["ct"] = hash_data(city.lower().replace(" ", ""))

    # Event Data
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "event_source_url": event_source_url,
        "user_data": user_data,
    }

    if custom_data:
        event_data["custom_data"] = custom_data

    # Wrapper
    payload = {"data": [event_data], "access_token": settings.META_ACCESS_TOKEN}

    if settings.TEST_EVENT_CODE:
        payload["test_event_code"] = settings.TEST_EVENT_CODE

    return payload


# =================================================================
# SYNC VS ASYNC SENDERS
# =================================================================


def send_event(
    event_name: str,
    event_source_url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    fbclid: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
) -> bool:
    """Synchronous Sender (For Celery Tasks) - Uses Persistent Connection Pooling"""

    # 🚀 Redis Deduplication Check (Ultra-fast, <5ms)
    if not deduplicate_event(event_id, event_name):
        logger.info(f"🔄 [DEDUP] Skipped duplicate {event_name}: {event_id[:16]}...")
        return True  # Return True since original was already sent

    # Sandbox Check
    if settings.META_SANDBOX_MODE:
        logger.info(f"🛡️ [SANDBOX] Intercepted {event_name}")
        return True

    payload = _build_payload(
        event_name,
        event_source_url,
        client_ip,
        user_agent,
        event_id,
        fbclid,
        fbp,
        external_id,
        phone,
        email,
        custom_data,
    )

    try:
        response = sync_client.post(settings.meta_api_url, json=payload)

        if response.status_code == 200:
            logger.info(f"[META CAPI] ✅ {event_name} sent via HTTP/2")
            return True
        else:
            logger.warning(f"[META CAPI] ⚠️ {event_name} Failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"[META CAPI] ❌ Error: {e}")
        return False


async def send_event_async(
    event_name: str,
    event_source_url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    fbclid: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
) -> bool:
    """Asynchronous Sender (For FastAPI Routes) - Non-Blocking"""

    if settings.META_SANDBOX_MODE:
        logger.info(f"🛡️ [SANDBOX ASYNC] Intercepted {event_name}")
        return True

    payload = _build_payload(
        event_name,
        event_source_url,
        client_ip,
        user_agent,
        event_id,
        fbclid,
        fbp,
        external_id,
        phone,
        email,
        custom_data,
    )

    try:
        if async_client is None:
            async with httpx.AsyncClient(timeout=timeout, http2=True) as client:
                response = await client.post(settings.meta_api_url, json=payload)
        else:
            response = await async_client.post(settings.meta_api_url, json=payload)

        if response.status_code == 200:
            logger.info(f"[META CAPI ASYNC] ✅ {event_name} sent via HTTP/2")
            return True
        else:
            logger.warning(f"[META CAPI ASYNC] ⚠️ {event_name} Failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"[META CAPI ASYNC] ❌ Error: {e}")
        return False


# =================================================================
# n8n WEBHOOKS
# =================================================================


def send_n8n_webhook(event_data: Dict[str, Any]) -> bool:
    """Sync Webhook for n8n (Celery)"""
    if not settings.N8N_WEBHOOK_URL:
        return False

    try:
        response = sync_client.post(settings.N8N_WEBHOOK_URL, json=event_data)
        if response.status_code == 200:
            logger.info("✅ n8n Webhook sent via HTTP/2")
            return True
    except Exception as e:
        logger.warning(f"⚠️ n8n Error: {e}")
    return False


# =================================================================
# API SHORTCUTS (Sync by default for now, can add async later)
# =================================================================


def track_lead(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    source: str,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None,
) -> bool:
    """Send Lead Event"""
    custom_data = {"content_name": source, "content_category": "lead", "lead_source": source}

    if service_data:
        custom_data.update(
            {
                "content_name": service_data.get("name", source),
                "content_ids": [service_data.get("id")] if service_data.get("id") else [],
                "content_category": service_data.get("intent", "lead"),
                "trigger_location": source,
            }
        )

    return send_event(
        event_name="Lead",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data,
    )


# =================================================================
# 🚀 ENHANCED FUNNEL TRACKING
# =================================================================


def track_view_content(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    content_name: str,
    content_category: str = "service",
    content_id: Optional[str] = None,
    fbclid: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
) -> bool:
    """
    Track ViewContent - When user views a specific service.
    Helps Meta know which services are popular.

    Usage: Fire when user scrolls to service section or clicks service card.
    """
    custom_data = {
        "content_name": content_name,
        "content_category": content_category,
        "content_type": "product",
        "currency": "BOB",
    }

    if content_id:
        custom_data["content_ids"] = [content_id]

    return send_event(
        event_name="ViewContent",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        fbp=fbp,
        external_id=external_id,
        custom_data=custom_data,
    )


def track_initiate_contact(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    contact_method: str = "whatsapp",
    service_interest: Optional[str] = None,
    fbclid: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
) -> bool:
    """
    Track InitiateContact - Right before WhatsApp redirect.
    More specific than Lead, shows clear purchase intent.

    Usage: Fire when user clicks WhatsApp button.
    """
    custom_data = {"contact_method": contact_method, "content_category": "consultation_request"}

    if service_interest:
        custom_data["content_name"] = service_interest

    return send_event(
        event_name="Contact",  # Standard Meta event
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        fbp=fbp,
        external_id=external_id,
        custom_data=custom_data,
    )


def track_scroll_depth(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    depth_percent: int,
    time_on_page_seconds: int,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None,
) -> bool:
    """
    Track scroll depth and time on page.
    Meta uses this to find engaged users.

    Usage: Fire when user scrolls 50%, 75%, or 100%.
    """
    custom_data = {
        "scroll_depth": depth_percent,
        "time_on_page": time_on_page_seconds,
        "engagement_level": "high"
        if depth_percent >= 75
        else "medium"
        if depth_percent >= 50
        else "low",
    }

    return send_event(
        event_name="CustomizeProduct",  # Using standard event for engagement
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data,
    )
