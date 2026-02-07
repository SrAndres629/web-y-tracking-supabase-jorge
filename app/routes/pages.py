# =================================================================
# PAGES.PY - Rutas de páginas HTML (FastAPI Background Tasks)
# Jorge Aguirre Flores Web
# =================================================================
import time
import logging
import os
from fastapi import APIRouter, Request, Response, BackgroundTasks, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.config import settings
from app.database import get_visitor_fbclid, save_visitor
from app.tracking import generate_external_id, generate_fbc, send_event
from app.cache import cache_visitor_data, get_cached_visitor
from app.services import get_services_config, get_contact_config

logger = logging.getLogger("BackgroundWorker")

router = APIRouter()

# Absolute path to templates (fixes Docker/Render path issues)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# 🕒 SILICON VALLEY VERSIONING: Unique ID per-process start
# This forces global cache bust when the app restarts (deploy)
SYSTEM_VERSION = str(int(time.time()))
templates.env.globals["system_version"] = SYSTEM_VERSION
logger.info(f"💎 SYSTEM CORE: Version {SYSTEM_VERSION} initialized.")


# =================================================================
# MINI-WORKERS (Execute after HTTP response)
# =================================================================

def bg_save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data):
    """Saves visitor without blocking page render"""
    try:
        save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data)
        logger.info(f"✅ [BG] Visitor saved: {external_id[:16]}...")
    except Exception as e:
        logger.error(f"❌ [BG] Error saving visitor: {e}")


def bg_send_pageview(event_source_url, client_ip, user_agent, event_id, fbclid, fbp, external_id, city=None, state=None, country=None):
    """Sends PageView to Meta CAPI via Official SDK (Elite Service)"""
    try:
        from app.meta_capi import send_elite_event
        
        # Construct fbc cookie if fbclid is present
        fbc_cookie = None
        if fbclid:
            import time
            timestamp = int(time.time())
            fbc_cookie = f"fb.1.{timestamp}.{fbclid}"

        result = send_elite_event(
            event_name="PageView",
            event_id=event_id,
            url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            external_id=external_id,
            fbc=fbc_cookie,
            fbp=fbp,
            city=city,
            state=state,
            country=country,
            custom_data={}
        )
        
        status = result.get("status")
        if status == "success":
            logger.info(f"✅ [BG] PageView sent to Meta CAPI")
        else:
            logger.warning(f"⚠️ [BG] PageView issue: {result}")

    except Exception as e:
        logger.error(f"❌ [BG] PageView error: {e}")


# =================================================================
# PAGE ROUTES
# =================================================================

@router.head("/", response_class=HTMLResponse)
async def head_root():
    """HEAD response for UptimeRobot (no tracking)"""
    return Response(status_code=200)


@router.get("/", response_class=HTMLResponse)
async def read_root( # noqa: C901
    request: Request, 
    response: Response,
    background_tasks: BackgroundTasks,
    # Auto-capture cookies for EMQ
    fbp_cookie: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc_cookie: Optional[str] = Cookie(default=None, alias="_fbc")
):
    """
    PÁGINA DE INICIO
    - Captura fbclid de Meta Ads
    - Envía PageView a CAPI (Background)
    - Persiste visitante en PostgreSQL (Background)
    
    SPEED: Template returns INSTANTLY, tracking runs after.
    """
    # 0. A/B TESTING (Silicon Valley Science)
    # Randomly assign variant if not present in cookie
    ab_variant = request.cookies.get("ab_test_group")
    if not ab_variant:
        import random
        ab_variant = "variant_b" if random.random() > 0.5 else "variant_a"
        
    # 0.1 FETCH DYNAMIC CONTENT (Phase 14 - Agility Engine)
    services_config = await get_services_config()
    contact_config = await get_contact_config()

    # 1. SETUP & IDENTITY
    start_time = time.time()
    timings = {}
    event_id = str(int(time.time() * 1000))
    
    # 🛡️ Real IP & Geo Extraction (Cloudflare)
    # Architecture: Zero-Latency Data Enrichment via Edge Headers
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    
    # Cloudflare Geo Headers (Free Enterprise-grade IP Intelligence)
    cf_country = request.headers.get("cf-ipcountry")
    cf_city = request.headers.get("cf-ipcity")
    cf_region = request.headers.get("cf-region") or request.headers.get("cf-region-code")
    
    if cf_ip:
        client_ip = cf_ip
    elif forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host
    
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # =================================================================
    # ⚡ TTFB OPTIMIZATION (Phase 5)
    # logic: Check Cookies -> Check URL -> (Only if needed) Check DB
    # =================================================================
    # =================================================================
    # 7. DYNAMIC LANDING (SILICON VALLEY UX)
    # =================================================================
    # Context-Aware Hero Section based on Ads
    utm_campaign = request.query_params.get('utm_campaign', '').lower()
    utm_content = request.query_params.get('utm_content', '').lower()
    
    # Default Hero (General)
    hero_content = {
        "title": 'Ingeniería de la <span class="italic font-light text-gradient-gold">Mirada</span>',
        "subtitle": "Especialista en Microblading",
        "bg_class": "bg-luxury-black", # Default dark
        "is_dynamic": False
    }

    # Dynamic Logic
    if 'labios' in utm_campaign or 'lips' in utm_campaign:
        hero_content = {
            "title": 'Arte y Volumen en tus <span class="italic font-light text-gradient-gold">Labios</span>',
            "subtitle": "Micropigmentación Full Color",
            "bg_class": "bg-luxury-black", 
            "is_dynamic": True
        }
    elif 'ojos' in utm_campaign or 'delineado' in utm_campaign or 'eyes' in utm_campaign:
        hero_content = {
            "title": 'Tu Mirada, Perfectamente <span class="italic font-light text-gradient-gold">Delineada</span>',
            "subtitle": "Delineado Permanente de Ojos",
            "bg_class": "bg-luxury-black",
            "is_dynamic": True
        }
    elif 'cejas' in utm_campaign or 'brows' in utm_campaign:
        hero_content = {
             "title": 'Cejas Perfectas, <span class="italic font-light text-gradient-gold">Pelo a Pelo</span>',
             "subtitle": "Microblading 3D Hiper-Realista",
             "bg_class": "bg-luxury-black",
             "is_dynamic": True
        }

    # 1. Generate Visitor ID (Determinstic from IP + UA)
    # =================================================================
    external_id = generate_external_id(client_ip, user_agent)

    # 1. Try to get fbclid from URL (Highest Priority)
    fbclid = request.query_params.get('fbclid')
    
    # 2. If not in URL, try to get from _fbc cookie (Fastest - No DB)
    fbp = fbp_cookie
    if not fbclid and fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
            logger.debug(f"🍪 Recovered fbclid from cookie: {fbclid}")

    # 3. Try Redis Cache (Elite Speed: <10ms)
    t0_cache = time.time()
    if not fbclid:
        cached_data = get_cached_visitor(external_id)
        if cached_data:
            fbclid = cached_data.get("fbclid")
            if fbclid:
                logger.debug(f"⚡ Recovered fbclid from REDIS: {fbclid}")
    timings["cache_ms"] = int((time.time() - t0_cache) * 1000)
    logger.info(f"⏱️ [Perf] Cache Lookup: {timings['cache_ms']}ms")

    # 4. If still not found, try to recover from DB (slower, use async wrapper)
    t0_db = time.time()
    if not fbclid:
        try:
            # 🚀 ThreadPool to prevent blocking Event Loop
            from starlette.concurrency import run_in_threadpool
            fbclid = await run_in_threadpool(get_visitor_fbclid, external_id)
            if fbclid:
                 logger.debug(f"🔍 Recovered fbclid from DB: {fbclid}")
        except Exception as e:
            logger.warning(f"⚠️ DB Warning: Could not retrieve fbclid: {e}")
            fbclid = None
    timings["db_ms"] = int((time.time() - t0_db) * 1000)
    logger.info(f"⏱️ [Perf] DB Lookup: {timings['db_ms']}ms")
    
    # 5. Link fbc cookie (DISABLED SERVER-SIDE TO ENABLE CDN CACHING)
    # logic: Setting a cookie here bypasses Vercel/Cloudflare Cache.
    # The client-side tracking.js already handles cookie persistence.
    # if fbclid:
    #     fbc_value = generate_fbc(fbclid)
    #     response.set_cookie(...)
    
    # =================================================================
    # BACKGROUND TASKS (Run AFTER response is sent)
    # =================================================================
    
    # 1. Save Visitor to DB & Cache
    background_tasks.add_task(
        bg_save_visitor,
        external_id=external_id,
        fbclid=fbclid or "",
        client_ip=client_ip,
        user_agent=user_agent,
        source="pageview",
        utm_data={
            'utm_source': request.query_params.get('utm_source'),
            'utm_medium': request.query_params.get('utm_medium'),
            'utm_campaign': request.query_params.get('utm_campaign'),
        }
    )
    
    # Update cache if we have new data
    if fbclid:
        background_tasks.add_task(cache_visitor_data, external_id, {"fbclid": fbclid})

    # 2. Send PageView to Meta CAPI (With Geo Data)
    background_tasks.add_task(
        bg_send_pageview,
        event_source_url=current_url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        fbp=fbp,
        external_id=external_id,
        city=cf_city,
        state=cf_region,
        country=cf_country
    )
    
    # Server-Timing Headers for Debugging
    total_ms = int((time.time() - start_time) * 1000)
    logger.info(f"⏱️ [Perf] Total Processing: {total_ms}ms (Cache: {timings.get('cache_ms', 0)}ms, DB: {timings.get('db_ms', 0)}ms)")
    timing_header = f"total;dur={total_ms}, cache;dur={timings.get('cache_ms', 0)}, db;dur={timings.get('db_ms', 0)}"

    # 🚀 SILICON VALLEY CACHING (Enable Cloudflare EDGE Cache)
    # public: allow caching by CDN
    # s-maxage: Cloudflare edge cache duration (1 week)
    # stale-while-revalidate: Serve old content while updating in background (60s)
    
    # 🛡️ SILICON VALLEY SYNCHRONICITY: Force revalidation of HTML
    # This ensures users ALWAYS get the latest HTML which then loads the latest Assets (?v=)
    headers = {
        "Server-Timing": timing_header,
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    # RESPONSE WITH COOKIE
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "pixel_id": settings.META_PIXEL_ID,
            "pageview_event_id": event_id,
            "external_id": external_id,
            "fbclid": fbclid or "", # Pass to frontend for contact button
            "services": services_config,
            "contact": contact_config,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "clarity_id": settings.CLARITY_PROJECT_ID,
            "flags": {
                "show_testimonials": settings.FLAG_SHOW_TESTIMONIALS,
                "show_gallery": settings.FLAG_SHOW_GALLERY,
                "enable_chat_widget": settings.FLAG_ENABLE_CHAT_WIDGET,
                "cta_variant": settings.FLAG_CTA_VARIANT,
                "hero_style": settings.FLAG_HERO_STYLE,
                "meta_tracking": settings.FLAG_META_TRACKING,
                "maintenance_mode": settings.FLAG_MAINTENANCE_MODE,
                "booking_enabled": settings.FLAG_BOOKING_ENABLED,
            },
            # 🧠 UX: Dynamic Hero Data
            "hero_content": hero_content,
            "ab_variant": ab_variant # Pass to template for UI logic
        },
        headers=headers
    )
    response.set_cookie(key="ab_test_group", value=ab_variant, max_age=2592000) # 30 days
    return response
