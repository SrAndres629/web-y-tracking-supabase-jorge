# =================================================================
# TRACKING.PY - Meta Conversions API (CAPI) - High Performance
# Jorge Aguirre Flores Web
# =================================================================
import hashlib
import logging
import os
import random
import time
from typing import Any, Dict, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.database import save_emq_score
from app.domain.services.emq_monitor import emq_monitor
from app.domain.validation.event_validator import event_validator

# Configure Logging
logger = logging.getLogger("uvicorn.error")

# 🚀 Redis Cache for Ultra-Fast Deduplication (MVP Phase 1)
try:
    from app.infrastructure.persistence.deduplication_service import dedup_service

    def try_consume_event(event_id: str, event_name: str = "event") -> bool:
        """Attempt to consume event ID using Redis."""
        return dedup_service.try_consume_event(event_id, event_name)

    def cache_visitor_data(_external_id: str, _data: Dict[str, Any], _ttl_hours: int = 24) -> None:
        """Cache visitor data in Redis."""
        try:
            dedup_service.cache_visitor(_external_id, _data, ttl=_ttl_hours * 3600)
        except AttributeError:
            pass  # Fallback if method missing in mock

    def get_cached_visitor(_external_id: str) -> Optional[Dict[str, Any]]:
        """Get cached visitor data from Redis."""
        try:
            return dedup_service.get_visitor(_external_id)
        except AttributeError:
            return None

    CACHE_ENABLED = True
except ImportError as e:
    logger.warning("⚠️ Deduplication Service Import Error: %s", str(e))
    CACHE_ENABLED = False

    # Fallback Logic (In-Memory for Dev/Test)
    _memory_dedup = {}

    def try_consume_event(event_id: str, event_name: str = "event") -> bool:
        if event_id in _memory_dedup:
            return False
        _memory_dedup[event_id] = time.time()
        return True

    def cache_visitor_data(_external_id: str, _data: Dict[str, Any], _ttl_hours: int = 24) -> None:
        pass

    def get_cached_visitor(_external_id: str) -> Optional[Dict[str, Any]]:
        return None


# =================================================================
# HTTP CLIENTS (SINGLETONS FOR PERSISTENT POOLING)
# =================================================================
# reusing clients enables HTTP/2 and avoids SSL Handshake overhead (save ~200ms)


timeout = httpx.Timeout(10.0, connect=5.0)
sync_client = httpx.Client(timeout=timeout, http2=True)

# Async client for FastAPI routes (future proofing)
_AUDIT_MODE = os.getenv("AUDIT_MODE", "").strip() == "1"
async_client = None if _AUDIT_MODE else httpx.AsyncClient(timeout=timeout, http2=True)

# =================================================================
# HASHING FUNCTIONS
# =================================================================


def hash_data(data: str) -> str:
    """Atomic Hash: Fast, efficient, and cached."""
    return hashlib.sha256(data.encode()).hexdigest()


def generate_fbc(fbclid: str) -> str:
    """Generates standard Meta fbc string: fb.1.timestamp.fbclid"""
    return f"fb.1.{int(time.time())}.{fbclid}"


def generate_event_id(event_name: str, external_id: str) -> str:
    """Generates a unique, deterministic event ID for deduplication."""
    raw = f"{event_name}_{external_id}_{int(time.time() / 60)}"
    return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()  # nosec B303


def generate_fbp() -> str:
    """Generate fbp parameter (Browser Display ID)"""
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    return f"fb.1.{timestamp}.{random_id}"


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


def _log_emq(event_name: str, payload: Dict[str, Any], client_id: Optional[str] = None):
    """Calculates, logs, and persists Event Match Quality Score."""
    try:
        data_block = payload.get("data", [{}])[0]
        user_data = data_block.get("user_data", {})
        score = emq_monitor.evaluate(user_data)
        level = emq_monitor.get_quality_level(score)

        if score < 4.0:
            logger.warning(
                "📉 [EMQ WARNING] %s: Score %s/10 (%s) - Missing Strong IDs",
                event_name,
                score,
                level,
            )
        else:
            logger.info("📊 [EMQ] %s: %s/10 (%s)", event_name, score, level)

        # 🚀 Persist for Dashboard
        import json

        payload_size = len(json.dumps(payload))
        has_pii = any(k in user_data for k in ["em", "ph", "fn", "ln"])

        save_emq_score(client_id, event_name, score, payload_size, has_pii)
        return score
    except (TypeError, ValueError, json.JSONDecodeError, AttributeError) as e:
        logger.warning("⚠️ EMQ Calc Error: %s", str(e))
        return 0.0


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
    custom_data: Optional[Dict[str, Any]] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    fb_browser_id: Optional[str] = None,
    access_token: Optional[str] = None,
    fbc: Optional[str] = None,
) -> Dict[str, Any]:
    """Constructs the JSON payload for Meta CAPI with Enhanced Matching"""

    # 🔍 PRE-VALIDATION: Check raw inputs
    warnings = event_validator.check_pre_hashing(email=email or "", phone=phone or "")
    for warning in warnings:
        logger.warning(f"⚠️ [VALIDATION] {warning}")

    # User Data (Advanced Matching)
    user_data = {
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }

    if external_id:
        user_data["external_id"] = hash_data(external_id)
    if fbc:
        user_data["fbc"] = fbc
    elif fbclid:
        user_data["fbc"] = generate_fbc(fbclid)

    if fbp:
        user_data["fbp"] = fbp
    if fb_browser_id:
        user_data["fb_browser_id"] = fb_browser_id
    if phone:
        clean_phone = "".join(filter(str.isdigit, phone))
        if not clean_phone.startswith("591"):
            clean_phone = "591" + clean_phone
        user_data["ph"] = hash_data(clean_phone)
    if email:
        user_data["em"] = hash_data(email)

    if country:
        user_data["country"] = hash_data(country.lower())
    else:
        user_data["country"] = hash_data("bo")

    if city:
        user_data["ct"] = hash_data(city.lower().replace(" ", ""))
    if state:
        user_data["st"] = hash_data(state.lower().replace(" ", ""))
    if zip_code:
        user_data["zp"] = hash_data(zip_code.replace(" ", ""))
    if first_name:
        user_data["fn"] = hash_data(first_name.lower())
    if last_name:
        user_data["ln"] = hash_data(last_name.lower())

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

    payload = {
        "data": [event_data],
        "access_token": access_token or settings.META_ACCESS_TOKEN,
    }

    is_production = os.getenv("VERCEL_ENV") == "production"
    if settings.TEST_EVENT_CODE and not is_production:
        payload["test_event_code"] = settings.TEST_EVENT_CODE

    return payload


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
)
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
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    access_token: Optional[str] = None,
    pixel_id: Optional[str] = None,
    client_id: Optional[str] = None,
    fbc: Optional[str] = None,
) -> bool:
    """Sends event to Meta CAPI via HTTP (Sync)"""

    if not try_consume_event(event_id, event_name):
        logger.info("🔄 [DEDUP] Skipped duplicate %s", event_name)
        return True

    if settings.META_SANDBOX_MODE:
        logger.info("🛡️ [SANDBOX] Intercepted %s", event_name)
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
        country=country,
        city=city,
        state=state,
        zip_code=zip_code,
        first_name=first_name,
        last_name=last_name,
        access_token=access_token,
        fbc=fbc,
    )

    api_url = settings.meta_api_url
    if pixel_id:
        api_url = f"https://graph.facebook.com/v21.0/{pixel_id}/events"

    _log_emq(event_name, payload, client_id=client_id)

    if not event_validator.validate_payload(payload):
        logger.error("❌ [VALIDATION FAILED] Payload rejected for %s", event_name)

    try:
        response = sync_client.post(api_url, json=payload)
        if response.status_code == 200:
            logger.info("[META CAPI] ✅ %s sent via HTTP/2", event_name)
            return True
        else:
            logger.warning(
                "[META CAPI] ⚠️ %s Failed (%d): %s",
                event_name,
                response.status_code,
                response.text,
            )
            return False
    except Exception:
        logger.exception("[META CAPI] ❌ Error")
        raise


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
)
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
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    access_token: Optional[str] = None,
    pixel_id: Optional[str] = None,
    client_id: Optional[str] = None,
    fbc: Optional[str] = None,
) -> bool:
    """Asynchronous Sender (For FastAPI Routes)"""

    if not try_consume_event(event_id, event_name):
        logger.info("🔄 [DEDUP ASYNC] Skipped duplicate %s", event_name)
        return True

    if settings.META_SANDBOX_MODE:
        logger.info("🛡️ [SANDBOX ASYNC] Intercepted %s", event_name)
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
        country=country,
        city=city,
        state=state,
        zip_code=zip_code,
        first_name=first_name,
        last_name=last_name,
        access_token=access_token,
        fbc=fbc,
    )

    api_url = settings.meta_api_url
    if pixel_id:
        api_url = f"https://graph.facebook.com/v21.0/{pixel_id}/events"

    _log_emq(event_name, payload, client_id=client_id)

    if not event_validator.validate_payload(payload):
        logger.error("❌ [VALIDATION FAILED] Payload rejected for %s", event_name)

    try:
        if async_client is None:
            async with httpx.AsyncClient(timeout=timeout, http2=True) as client:
                response = await client.post(api_url, json=payload)
        else:
            response = await async_client.post(api_url, json=payload)

        if response.status_code == 200:
            logger.info("[META CAPI ASYNC] ✅ %s sent via HTTP/2", event_name)
            return True
        else:
            logger.warning(
                "[META CAPI ASYNC] ⚠️ %s Failed (%d): %s",
                event_name,
                response.status_code,
                response.text,
            )
            return False
    except Exception:
        logger.exception("[META CAPI ASYNC] ❌ Error")
        raise


def send_n8n_webhook(event_data: Dict[str, Any]) -> bool:
    """Sync Webhook for n8n"""
    if not settings.N8N_WEBHOOK_URL:
        return False
    try:
        response = sync_client.post(settings.N8N_WEBHOOK_URL, json=event_data)
        if response.status_code == 200:
            logger.info("✅ n8n Webhook sent via HTTP/2")
            return True
    except Exception as e:
        logger.warning("⚠️ n8n Error: %s", str(e))
    return False


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
    custom_data: Dict[str, Any] = {
        "content_name": source,
        "content_category": "lead",
        "lead_source": source,
    }
    if service_data:
        custom_data.update(
            {
                "content_name": str(service_data.get("name", source)),
                "content_ids": ([str(service_data.get("id"))] if service_data.get("id") else []),
                "content_category": str(service_data.get("intent", "lead")),
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
    """Track ViewContent"""
    custom_data: Dict[str, Any] = {
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
    """Track InitiateContact"""
    custom_data = {
        "contact_method": contact_method,
        "content_category": "consultation_request",
    }
    if service_interest:
        custom_data["content_name"] = service_interest
    return send_event(
        event_name="Contact",
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
    """Track scroll depth"""
    custom_data = {
        "scroll_depth": depth_percent,
        "time_on_page": time_on_page_seconds,
        "engagement_level": (
            "high" if depth_percent >= 75 else "medium" if depth_percent >= 50 else "low"
        ),
    }
    return send_event(
        event_name="CustomizeProduct",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data,
    )
