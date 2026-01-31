# =================================================================
# TRACKING.PY - Meta Conversions API (CAPI) - High Performance
# Jorge Aguirre Flores Web
# =================================================================
import hashlib
import time
import httpx
import asyncio
from typing import Optional, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# =================================================================
# HTTP CLIENTS (SINGLETONS FOR PERSISTENT POOLING)
# =================================================================
# reusing clients enables HTTP/2 and avoids SSL Handshake overhead (save ~200ms)
timeout = httpx.Timeout(10.0, connect=5.0)
sync_client = httpx.Client(timeout=timeout, http2=True)

# Async client for FastAPI routes (future proofing)
async_client = httpx.AsyncClient(timeout=timeout, http2=True)

# =================================================================
# HASHING FUNCTIONS
# =================================================================

def hash_data(value: str) -> Optional[str]:
    """Hash SHA256 for user data (Meta requirement)"""
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()


def generate_external_id(ip: str, user_agent: str) -> str:
    """Generate deterministic ID based on IP + UA"""
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32]


def generate_fbc(fbclid: str) -> Optional[str]:
    """Generate fbc parameter"""
    if not fbclid:
        return None
    timestamp = int(time.time())
    return f"fb.1.{timestamp}.{fbclid}"


def extract_fbclid_from_fbc(fbc_cookie: str) -> Optional[str]:
    """Extract fbclid from cookie"""
    if not fbc_cookie or not fbc_cookie.startswith("fb.1."):
        return None
    
    parts = fbc_cookie.split(".")
    if len(parts) >= 4:
        return parts[3]
    return None


# =================================================================
# META CONVERSIONS API (CORE LOGIC)
# =================================================================

def _build_payload(
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
    custom_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Constructs the JSON payload for Meta CAPI"""
    
    # User Data
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
    if phone:
        clean_phone = "".join(filter(str.isdigit, phone))
        user_data["ph"] = hash_data(clean_phone)
    if email:
        user_data["em"] = hash_data(email)
    
    # Event Data
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "event_source_url": event_source_url,
        "user_data": user_data
    }
    
    if custom_data:
        event_data["custom_data"] = custom_data
    
    # Wrapper
    payload = {
        "data": [event_data],
        "access_token": settings.META_ACCESS_TOKEN
    }
    
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
    custom_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Synchronous Sender (For Celery Tasks) - Uses Persistent Connection Pooling"""
    
    # Sandbox Check
    if settings.META_SANDBOX_MODE:
        logger.info(f"🛡️ [SANDBOX] Intercepted {event_name}")
        return True

    payload = _build_payload(
        event_name, event_source_url, client_ip, user_agent, event_id,
        fbclid, fbp, external_id, phone, email, custom_data
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
    custom_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Asynchronous Sender (For FastAPI Routes) - Non-Blocking"""

    if settings.META_SANDBOX_MODE:
        logger.info(f"🛡️ [SANDBOX ASYNC] Intercepted {event_name}")
        return True

    payload = _build_payload(
        event_name, event_source_url, client_ip, user_agent, event_id,
        fbclid, fbp, external_id, phone, email, custom_data
    )

    try:
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
            logger.info(f"✅ n8n Webhook sent via HTTP/2")
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
    service_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Send Lead Event"""
    custom_data = {
        "content_name": source,
        "content_category": "lead",
        "lead_source": source
    }
    
    if service_data:
        custom_data.update({
            "content_name": service_data.get("name", source),
            "content_ids": [service_data.get("id")] if service_data.get("id") else [],
            "content_category": service_data.get("intent", "lead"),
            "trigger_location": source
        })
    
    return send_event(
        event_name="Lead",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data
    )
