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
from app.services import SERVICES_CONFIG, CONTACT_CONFIG

logger = logging.getLogger("BackgroundWorker")

router = APIRouter()

# Absolute path to templates (fixes Docker/Render path issues)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)


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
async def read_root(
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
    
    # 5. Link fbc cookie if we found fbclid
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(
            key="_fbc", 
            value=fbc_value, 
            max_age=7776000,  # 90 days
            httponly=True, 
            samesite="lax",
            secure=True
        )
    
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
    timing_header = f"total;dur={total_ms}, cache;dur={timings.get('cache_ms', 0)}, db;dur={timings.get('db_ms', 0)}"

    # 🚀 INSTANT RESPONSE (Background tasks run after this)
    resp = templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": settings.META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or "", # Pass to frontend for contact button
        "services": SERVICES_CONFIG,
        "contact": CONTACT_CONFIG,
        # 🚀 Identity Resolution (Phase 7)
        "google_client_id": settings.GOOGLE_CLIENT_ID,
        "clarity_id": settings.CLARITY_PROJECT_ID,
        # 🚩 Feature Flags (Control from Vercel Dashboard)
        "flags": {
            "show_testimonials": settings.FLAG_SHOW_TESTIMONIALS,
            "show_gallery": settings.FLAG_SHOW_GALLERY,
            "enable_chat_widget": settings.FLAG_ENABLE_CHAT_WIDGET,
            "cta_variant": settings.FLAG_CTA_VARIANT,
            "hero_style": settings.FLAG_HERO_STYLE,
            "meta_tracking": settings.FLAG_META_TRACKING,
            "maintenance_mode": settings.FLAG_MAINTENANCE_MODE,
            "booking_enabled": settings.FLAG_BOOKING_ENABLED,
        }
    })
    
    # Apply Edge Caching & Performance Headers
    resp.headers["Cache-Control"] = "public, s-maxage=1, stale-while-revalidate=59"
    resp.headers["Server-Timing"] = timing_header
    
    return resp
