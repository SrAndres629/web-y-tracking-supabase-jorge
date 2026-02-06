import os
import httpx
import logging
import json
from typing import Optional, Dict, Any, List
from app.config import settings
from app.database import get_db_connection
from app.cache import redis_cache

# Configure Logging
logger = logging.getLogger("uvicorn.error")

QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")
VERCEL_URL = os.getenv("VERCEL_URL", "jorgeaguirreflores.com") 
if "http" not in VERCEL_URL:
    VERCEL_URL = f"https://{VERCEL_URL}"

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
    CACHE_TTL = 3600 # 1 hour
    
    # 🛡️ DEFENSIVE FALLBACKS (In case DB is empty/broken)
    _FALLBACKS = {
        "services_config": [
            {"id": "microblading", "title": "Microblading Elite", "description": "Cejas perfectas pelo a pelo.", "icon": "fa-eye", "color": "luxury-gold"},
            {"id": "eyeliner", "title": "Delineado Permanente", "description": "Resalta tu mirada.", "icon": "fa-pencil", "color": "luxury-gold"},
            {"id": "lips", "title": "Acuarela de Labios", "description": "Color vibrante para tus labios.", "icon": "fa-kiss", "color": "luxury-gold"}
        ],
        "contact_config": {
            "whatsapp": "https://wa.me/59164714751",
            "phone": "+591 64714751",
            "email": "contacto@jorgeaguirreflores.com",
            "location": "Santa Cruz de la Sierra",
            "instagram": "https://instagram.com/jorgeaguirreflores"
        }
    }

    @classmethod
    async def get_content(cls, key: str) -> Any:
        """Entry point for all dynamic content"""
        # 1. ⚡ RAM FIRST (No I/O)
        if key in cls._ram_cache:
            return cls._ram_cache[key]
        
        # 2. 🌀 REDIS SECOND (Shared between instances)
        try:
            cached = await redis_cache.get_json(f"content:{key}")
            if cached:
                cls._ram_cache[key] = cached
                return cached
        except:
            pass
            
        # 3. 🧬 DATABASE LAST (Source of Truth)
        content = cls._fetch_from_db(key)
        
        if content:
            # Update caches
            cls._ram_cache[key] = content
            try:
                await redis_cache.set_json(f"content:{key}", content, expire=cls.CACHE_TTL)
            except:
                pass
            return content
            
        # 4. 🛟 EMERGENCY FALLBACK
        return cls._FALLBACKS.get(key)

    @classmethod
    def _fetch_from_db(cls, key: str) -> Optional[Any]:
        """Synchronous DB fetch (Used for cold starts or refresh)"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT value FROM site_content WHERE key = %s", (key,))
                    row = cur.fetchone()
                    if row and row[0]:
                        # value is already JSON in DB, psycopg2 parses it if using jsonb
                        val = row[0]
                        return json.loads(val) if isinstance(val, str) else val
        except Exception as e:
            logger.error(f"❌ CMS DB Fetch Error ({key}): {e}")
        return None

    @classmethod
    async def warm_cache(cls):
        """Pre-loads all content into RAM. Called on FastAPI Startup."""
        logger.info("🔥 Warming up Zero-Latency CMS cache...")
        for key in cls._FALLBACKS.keys():
            content = await cls.get_content(key)
            if content:
                logger.debug(f"✅ Loaded {key}")
        logger.info("👑 CMS Cache Ready (0ms latency enabled)")

    @classmethod
    async def refresh_all(cls):
        """Clears L1/L2 cache. Forces L3 reload."""
        cls._ram_cache.clear()
        for key in cls._FALLBACKS.keys():
            try:
                await redis_cache.delete(f"content:{key}")
            except:
                pass
        await cls.warm_cache()

# =================================================================
# LEGACY WRAPPERS (To avoid breaking templates/routes)
# =================================================================

async def get_services_config() -> List[dict]:
    return await ContentManager.get_content("services_config")

async def get_contact_config() -> dict:
    return await ContentManager.get_content("contact_config")

# =================================================================
# CORE UTILITIES
# =================================================================

async def publish_to_qstash(event_data: dict):
    """Publishes an event to QStash to be processed asynchronously."""
    if not QSTASH_TOKEN:
        logger.warning("⚠️ QStash Token missing!")
        return False
    url = f"{VERCEL_URL}/api/hooks/process-event"
    headers = {"Authorization": f"Bearer {QSTASH_TOKEN}", "Content-Type": "application/json", "Upstash-Retries": "3"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"https://qstash.upstash.io/v2/publish/{url}", headers=headers, json=event_data, timeout=5.0)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"❌ QStash Error: {str(e)}")
            return False

async def validate_turnstile(token: str) -> bool:
    """Validates a Cloudflare Turnstile token."""
    if not settings.TURNSTILE_SECRET_KEY: return True
    if not token: return False
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token}, timeout=5.0)
            return response.json().get("success", False)
        except Exception: return True

def normalize_pii(data: str, mode: str = "email") -> str:
    """Silicon Valley Hygiene: Clean and normalize PII before hashing."""
    if not data: return ""
    clean_data = data.strip().lower()
    if mode == "phone":
        clean_data = "".join(filter(str.isdigit, data))
        if len(clean_data) == 8: clean_data = "591" + clean_data
    return clean_data
