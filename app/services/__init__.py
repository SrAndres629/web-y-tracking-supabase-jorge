# import hashlib
import asyncio
import json
import logging
import os
import time
from typing import Any, Coroutine, Dict, List, Optional, cast

# from functools import lru_cache
import httpx
from starlette.concurrency import run_in_threadpool
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app import database as legacy_database
from app.cache import redis_cache
from app.config import settings

# Configure Logging
logger = logging.getLogger("uvicorn.error")

# from app.services.seo_engine import SEOEngine  # Imported but unused


QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")

_raw_url = os.getenv("VERCEL_URL", "jorgeaguirreflores.com")
VERCEL_URL = f"https://{_raw_url}" if "http" not in _raw_url else _raw_url


# =================================================================
# 🧠 ZERO-COST CONTENT MANAGER (THE SUPERSTAR PROTOCOL)
# =================================================================


class ContentManager:
    """
    Manages dynamic content with extreme performance logic.
    Layer 1: Python RAM (0ms)
    Layer 2: Upstash Redis (10ms)
    Layer 3: Supabase DB (Fallback)
    """

    _ram_cache: Dict[str, Any] = {}
    _cache_times: Dict[str, float] = {}
    CACHE_TTL = 3600  # 1 hour
    STALE_THRESHOLD = 300  # 5 minutes

    # 🛡️ DEFENSIVE FALLBACKS (In case DB is empty/broken)
    _FALLBACKS: Dict[str, Any] = {
        "services_config": [
            {
                "id": "microblading",
                "title": "Microblading 3D",
                "subtitle": "Efecto Pelo a Pelo",
                "description": (
                    "Técnica pelo a pelo para cejas ultra naturales. "
                    "Rellena huecos y recupera la forma joven de tu ceja."
                ),
                "icon": "fa-eye-dropper",
                "image": "/static/images/service_brows.webp",
                "rating": "4.9",
                "clients": "+620",
                "badges": ["Más Pedido", "100% Natural", "2-3 años"],
                "benefits": ["2 hrs sesión", "Sin dolor", "Retoque incluido"],
            },
            {
                "id": "eyeliner",
                "title": "Delineado Permanente",
                "subtitle": "Efecto Pestañas",
                "description": (
                    "Despierta con una mirada intensa y expresiva. "
                    "Olvídate de que se corra el maquillaje."
                ),
                "icon": "fa-eye",
                "image": "/static/images/service_eyes.webp",
                "rating": "4.9",
                "clients": "+480",
                "badges": ["Sin Dolor", "Efecto Pestañas", "2-3 años"],
                "benefits": ["1.5 hrs sesión", "Anestesia tópica", "Resultados inmediatos"],
            },
            {
                "id": "lips",
                "title": "Labios Full Color",
                "subtitle": "Corrección y Volumen",
                "description": (
                    "Correcciones y luce una boca jugosa y saludable. "
                    "Tu color perfecto sin retocarte."
                ),
                "icon": "fa-kiss-wink-heart",
                "image": "/static/images/service_lips.webp",
                "rating": "5.0",
                "clients": "+400",
                "badges": ["Premium", "Color Natural", "1-2 años"],
                "benefits": ["2 hrs sesión", "Corrige volumen", "Efecto rejuvenecedor"],
            },
        ],
        "contact_config": {
            "whatsapp": "https://wa.me/59164714751",
            "phone": "+591 647 14 751",
            "email": "info@jorgeaguirreflores.com",
            "address": "Santa Cruz de la Sierra, Bolivia",
            "maps_url": ("https://maps.google.com/?q=Santa+Cruz+de+la+Sierra+Bolivia"),
            "location": "Santa Cruz de la Sierra",
            "instagram": "https://instagram.com/jorgeaguirreflores",
            "facebook": "https://facebook.com/jorgeaguirreflores",
            "tiktok": "https://tiktok.com/@jorgeaguirreflores",
            "cta_text": (
                "Hola Jorge, vi su web y me interesa una valoración para micropigmentación."
            ),
            "cta_assessment": (
                "Hola Jorge, quiero agendar mi diagnóstico "
                "gratuito y ver la geometría de mi rostro."
            ),
        },
    }

    @classmethod
    async def get_content(cls, key: str) -> Any:
        """Entry point for all dynamic content - SWR Optimized (TTFB 0ms)"""
        current_time = time.time()
        audit_mode = os.getenv("AUDIT_MODE", "").strip() == "1"

        # 1. ⚡ RAM FIRST (0ms)
        if key in cls._ram_cache:
            # Check if stale
            last_fetch = cls._cache_times.get(key, 0)
            if current_time - last_fetch > cls.STALE_THRESHOLD:
                logger.info("🔄 [SWR] RAM stale for '%s'. Triggering refresh...", key)
                if not audit_mode:
                    coro = cast(Coroutine[Any, Any, Any], cls._refresh_in_background(key))
                    asyncio.create_task(coro)
            return cls._ram_cache[key]

        # 2. 🌀 REDIS SECOND (<15ms)
        try:
            cached = await redis_cache.get_json(f"content:{key}")
            if cached:
                cls._ram_cache[key] = cached
                cls._cache_times[key] = current_time
                if not audit_mode:
                    coro = cast(Coroutine[Any, Any, Any], cls._refresh_in_background(key))
                    asyncio.create_task(coro)
                return cached
        except Exception as e:
            logger.debug("Redis skip: %s", e)

        # 3. 🧬 DATABASE / FALLBACK (Zero-Latency Guarantee)
        if not audit_mode:
            coro = cast(Coroutine[Any, Any, Any], cls._refresh_in_background(key))
            asyncio.create_task(coro)

        return cls._FALLBACKS.get(key)

    @classmethod
    async def _refresh_in_background(cls, key: str) -> Optional[Any]:
        """Fetch from DB and update all caches"""
        t0 = time.time()
        try:
            content = await run_in_threadpool(cls._fetch_from_db, key)
            if content:
                content = cls._deep_validate(key, content)
                if content:
                    cls._ram_cache[key] = content
                    cls._cache_times[key] = time.time()
                    try:
                        await redis_cache.set_json(f"content:{key}", content, expire=cls.CACHE_TTL)
                        logger.debug(
                            "✅ [SWR] Cache updated for '%s' (%dms)",
                            key,
                            int((time.time() - t0) * 1000),
                        )
                    except Exception as e:
                        logger.debug("Cache write error: %s", e)
                    return content
        except Exception as e:
            logger.error("❌ [SWR] Background refresh error for '%s': %s", key, e)
        return None

    @classmethod
    def _deep_validate(cls, key: str, content: Any) -> Optional[Any]:
        """Performs structural validation on dynamic content"""
        if key == "services_config":
            if isinstance(content, list) and content:
                return cls._validate_services_list(content)
        elif key == "contact_config":
            if isinstance(content, dict) and "whatsapp" in content:
                return content
        else:
            return content  # Minimal validation for other keys
        return None

    @classmethod
    def _validate_services_list(cls, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deep validation for the services configuration list"""
        valid_items: List[Dict[str, Any]] = []
        fallback_cfg = cast(List[Dict[str, Any]], cls._FALLBACKS["services_config"])
        fallbacks = {str(s["id"]): s for s in fallback_cfg}

        for raw_item in content:
            if not isinstance(raw_item, dict) or "id" not in raw_item:
                continue

            item = raw_item
            base_id = str(item.get("id", ""))
            base_fallback = fallbacks.get(base_id, fallback_cfg[0])

            # Critical Repair logic: Ensure 'badges' and 'benefits' exist
            if "badges" not in item or not isinstance(item["badges"], list):
                item["badges"] = base_fallback["badges"]
                logger.warning(
                    "🩹 Injected fallback badges for service: %s", item.get("id", "unknown")
                )

            if "benefits" not in item or not isinstance(item["benefits"], list):
                item["benefits"] = base_fallback["benefits"]

            valid_items.append(item)
        return valid_items

    @classmethod
    def _fetch_from_db(cls, key: str) -> Optional[Any]:
        """Synchronous DB fetch (Used for cold starts or refresh)"""
        try:
            with legacy_database.get_cursor() as cur:
                cur.execute("SELECT value FROM site_content WHERE key = %s", (key,))
                row = cur.fetchone()
                if row and row[0]:
                    val = row[0]
                    return json.loads(val) if isinstance(val, str) else val
        except Exception as e:
            logger.error("❌ CMS DB Fetch Error (%s): %s", key, e)
        return None

    @classmethod
    async def warm_cache(cls) -> None:
        """Pre-loads all content into RAM. Called on FastAPI Startup."""
        logger.info("🔥 Warming up Zero-Latency CMS cache (Parallel execution)...")
        tasks = [cls.get_content(key) for key in cls._FALLBACKS.keys()]
        await asyncio.gather(*tasks)
        logger.info("👑 CMS Cache Ready (0ms latency enabled)")

    @classmethod
    async def refresh_all(cls) -> None:
        """Clears L1/L2 cache. Forces L3 reload."""
        cls._ram_cache.clear()
        for key in cls._FALLBACKS.keys():
            try:
                await redis_cache.delete(f"content:{key}")
            except Exception as e:
                logger.error("Error deleting Redis cache for %s: %s", key, e)
        await cls.warm_cache()


# =================================================================
# LEGACY WRAPPERS (To avoid breaking templates/routes)
# =================================================================


async def get_services_config() -> List[Dict[str, Any]]:
    """Legacy wrapper for services config"""
    content: Any = await ContentManager.get_content("services_config")
    return cast(List[Dict[str, Any]], content or [])


async def get_contact_config() -> Dict[str, Any]:
    """Legacy wrapper for contact config"""
    content: Any = await ContentManager.get_content("contact_config")
    return cast(Dict[str, Any], content or {})


# =================================================================
# CORE UTILITIES
# =================================================================


# 🛡️ RELIABILITY: Retry logic for transient failures (Step 3 MVP)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
    reraise=True,
)
async def publish_to_qstash(event_data: Dict[str, Any]) -> bool:
    """Publishes an event to QStash to be processed asynchronously."""
    if not QSTASH_TOKEN:
        logger.warning("⚠️ QStash Token missing!")
        return False
    url = f"{VERCEL_URL}/hooks/process-event"
    headers = {
        "Authorization": f"Bearer {QSTASH_TOKEN}",
        "Content-Type": "application/json",
        "Upstash-Retries": "3",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://qstash.upstash.io/v2/publish/{url}",
                headers=headers,
                json=event_data,
                timeout=5.0,
            )
            response.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        logger.error("❌ QStash HTTP Error: %s - %s", e.response.status_code, e.response.text)
        return False
    except httpx.RequestError as e:
        logger.error("❌ QStash Request Error: %s", e)
        return False
    except Exception as e:
        logger.error("❌ QStash Unexpected Error: %s", e)
        return False
    return False


async def validate_turnstile(token: str) -> bool:
    """Validates a Cloudflare Turnstile token."""
    if not settings.TURNSTILE_SECRET_KEY:
        if not getattr(validate_turnstile, "_warned", False):
            logger.warning("⚠️ TURNSTILE_SECRET_KEY not set — bot protection DISABLED.")
            validate_turnstile._warned = True
        return True
    if not token:
        return False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
                timeout=5.0,
            )
            return bool(response.json().get("success", False))
    except httpx.RequestError as e:
        logger.error("Turnstile validation request error: %s", e)
        return True  # Fail safe
    except Exception as e:
        logger.error("Turnstile validation unexpected error: %s", e)
        return True  # Fail safe
    return True  # Final fallback


# @lru_cache(maxsize=128)
# def _get_cached_hash(data: str) -> str:
#     """Atomic Hash: Fast, efficient, and cached."""
#     return hashlib.sha256(data.encode()).hexdigest()


def normalize_pii(data: str, mode: str = "email") -> str:
    """Silicon Valley Hygiene: Clean and normalize PII before hashing."""
    if not data:
        return ""
    clean_data = data.strip().lower()
    if mode == "phone":
        clean_data = "".join(filter(str.isdigit, data))
        if len(clean_data) == 8:
            clean_data = "591" + clean_data
    return clean_data
