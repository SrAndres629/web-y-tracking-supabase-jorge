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
from app.services import get_services_config, get_contact_config
from app.interfaces.api.dependencies import get_legacy_facade

logger = logging.getLogger("BackgroundWorker")

router = APIRouter()
legacy = get_legacy_facade()

# 🗄️ TEMPLATE CONFIG (Using Centralized Settings)
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRS)

# 🕒 SILICON VALLEY VERSIONING: Unique ID per-process start
# This forces global cache bust when the app restarts (deploy)
SYSTEM_VERSION = str(int(time.time()))
templates.env.globals["system_version"] = SYSTEM_VERSION
logger.info(f"💎 SYSTEM CORE: Version {SYSTEM_VERSION} initialized.")


# =================================================================
# MINI-WORKERS (Execute after HTTP response)
# =================================================================

def bg_save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data, email=None, phone=None):
    """Saves visitor without blocking page render"""
    try:
        legacy.save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data, email=email, phone=phone)
        logger.info(f"✅ [BG] Visitor saved: {external_id[:16]}...")
    except Exception as e:
        logger.error(f"❌ [BG] Error saving visitor: {e}")


async def bg_send_pageview(event_source_url, client_ip, user_agent, event_id, fbclid, fbp, external_id, city=None, state=None, country=None):
    """Sends PageView to Meta CAPI via Official SDK (Elite Service)"""
    try:
        # Construct fbc cookie if fbclid is present
        fbc_cookie = None
        if fbclid:
            timestamp = int(time.time())
            fbc_cookie = f"fb.1.{timestamp}.{fbclid}"

        result = await legacy.send_elite_event(
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
    request: Request, background_tasks: BackgroundTasks,
    fbp_cookie: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc_cookie: Optional[str] = Cookie(default=None, alias="_fbc")
):
    """PÁGINA DE INICIO - Optimized for Speed & Tracking."""
    # 1. Identity & Config
    ident = _extract_identity_info(request)
    ab_variant = _handle_ab_test(request)
    services_config = await get_services_config()
    contact_config = await get_contact_config()
    hero_content = _get_hero_content(request.query_params)
    
    # 2. Tracking Identity
    event_id = str(int(time.time() * 1000))
    external_id = legacy.generate_external_id(ident['ip'], ident['ua'])
    fbclid = await _resolve_fbclid_full(request, fbc_cookie, external_id)
    
    # 4. SEO Engine (Silicon Valley Research Standard)
    from app.services.seo_engine import SEOEngine
    
    # Page metadata
    seo_meta = SEOEngine.get_page_metadata("/", {
        "title": "Jorge Aguirre Flores | Experto en Microblading y Estética Avanzada",
        "description": "Transforma tu mirada con el mejor especialista en Microblading de Santa Cruz. 30 años de trayectoria garantizan resultados naturales y artísticos."
    })
    
    # Schemas
    schemas = [
        SEOEngine.get_global_schema(),
        SEOEngine.get_breadcrumb_schema([{"name": "Inicio", "path": "/"}])
    ]
    
    # 5. Background Tasks & Cookies
    _schedule_tracking(background_tasks, request, ident, external_id, fbclid, fbp_cookie, event_id)
    
    # 6. Build Response with optimized caching headers
    response = templates.TemplateResponse(
        request=request, name="pages/site/home.html",
        context={
            "pixel_id": settings.META_PIXEL_ID, "pageview_event_id": event_id,
            "external_id": external_id, "fbclid": fbclid or "",
            "zaraz_debug_key": os.getenv("ZARAZ_DEBUG_KEY"),
            "services": services_config, "contact": contact_config,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "clarity_id": settings.CLARITY_PROJECT_ID,
            "turnstile_site_key": settings.TURNSTILE_SITE_KEY,
            "flags": _get_feature_flags(),
            "hero_content": hero_content, "ab_variant": ab_variant,
            "seo": {
                **seo_meta,
                "json_ld": SEOEngine.generate_all_json_ld(schemas)
            }
        },
        headers={
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
            "CDN-Cache-Control": "public, max-age=3600",
            "Vercel-CDN-Cache-Control": "public, max-age=3600"
        }
    )
    _set_identity_cookies(response, ab_variant, ident, fbclid, fbp_cookie)
    return response


@router.get("/tracking-motor", response_class=HTMLResponse)
async def read_tracking_motor(
    request: Request, background_tasks: BackgroundTasks,
    fbp_cookie: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc_cookie: Optional[str] = Cookie(default=None, alias="_fbc")
):
    """LANDING PAGE VENTA TRACKING ENGINE - Optimized for B2B Conversion."""
    # 1. Identity & Config
    ident = _extract_identity_info(request)
    services_config = await get_services_config()
    contact_config = await get_contact_config()
    
    # 2. Tracking Identity
    event_id = str(int(time.time() * 1000))
    external_id = legacy.generate_external_id(ident['ip'], ident['ua'])
    fbclid = await _resolve_fbclid_full(request, fbc_cookie, external_id)
    
    # 4. SEO Engine
    from app.services.seo_engine import SEOEngine
    
    seo_meta = SEOEngine.get_page_metadata("/tracking-motor", {
        "title": "Anti-Gravity Tracking Core | Meta CAPI Atomic Motor",
        "description": "Recupera el 40% de tu data perdida. El motor de tracking más avanzado con deduplicación atómica y EMQ Optimization."
    })
    
    schemas = [
        SEOEngine.get_global_schema(),
        SEOEngine.get_breadcrumb_schema([
            {"name": "Inicio", "path": "/"},
            {"name": "Tracking Motor", "path": "/tracking-motor"}
        ])
    ]
    
    # 5. Background Tasks
    _schedule_tracking(background_tasks, request, ident, external_id, fbclid, fbp_cookie, event_id)
    
    # 6. Build Response with optimized caching
    response = templates.TemplateResponse(
        request=request, name="pages/site/tracking_motor.html",
        context={
            "pixel_id": settings.META_PIXEL_ID, "pageview_event_id": event_id,
            "external_id": external_id, "fbclid": fbclid or "",
            "services": services_config, "contact": contact_config,
            "seo": {
                **seo_meta,
                "json_ld": SEOEngine.generate_all_json_ld(schemas)
            }
        },
        headers={
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
            "CDN-Cache-Control": "public, max-age=3600",
            "Vercel-CDN-Cache-Control": "public, max-age=3600"
        }
    )
    _set_identity_cookies(response, "variant_a", ident, fbclid, fbp_cookie)
    return response

@router.get("/onboarding", response_class=HTMLResponse)
async def read_onboarding(request: Request):
    """CLIENT ONBOARDING PAGE - Self-service credential generation."""
    from app.services.seo_engine import SEOEngine
    
    seo_meta = SEOEngine.get_page_metadata("/onboarding", {
        "title": "Onboarding | Atomic Tracking Motor",
        "description": "Configura tu motor de tracking y genera tu API Key en 5 minutos."
    })
    
    return templates.TemplateResponse(
        request=request, name="pages/site/onboarding.html",
        context={
            "seo": seo_meta,
            "services": await get_services_config(),
            "contact": await get_contact_config()
        }
    )

def _extract_identity_info(request: Request) -> dict:
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    return {
        "ip": cf_ip or (forwarded.split(",")[0].strip() if forwarded else request.client.host),
        "ua": request.headers.get('user-agent', ''),
        "country": request.headers.get("cf-ipcountry"),
        "city": request.headers.get("cf-ipcity"),
        "region": request.headers.get("cf-region") or request.headers.get("cf-region-code")
    }

def _handle_ab_test(request: Request) -> str:
    variant = request.cookies.get("ab_test_group")
    if not variant:
        import random
        variant = "variant_b" if random.random() > 0.5 else "variant_a"
    return variant

def _get_hero_content(params) -> dict:
    utm = params.get('utm_campaign', '').lower()
    content = {
        "title": 'Ingeniería de la <span class="italic font-light text-gradient-gold">Mirada</span>',
        "subtitle": "Especialista en Microblading", "bg_class": "bg-luxury-black", "is_dynamic": False
    }
    if 'labios' in utm or 'lips' in utm:
        content.update({"title": 'Arte y Volumen en tus <span class="italic font-light text-gradient-gold">Labios</span>', "subtitle": "Micropigmentación Full Color", "is_dynamic": True})
    elif 'ojos' in utm or 'delineado' in utm or 'eyes' in utm:
        content.update({"title": 'Tu Mirada, Perfectamente <span class="italic font-light text-gradient-gold">Delineada</span>', "subtitle": "Delineado Permanente de Ojos", "is_dynamic": True})
    elif 'cejas' in utm or 'brows' in utm:
        content.update({"title": 'Cejas Perfectas, <span class="italic font-light text-gradient-gold">Pelo a Pelo</span>', "subtitle": "Microblading 3D Hiper-Realista", "is_dynamic": True})
    return content

async def _resolve_fbclid_full(request, fbc_cookie, external_id):
    """
    Resolves FBCLID with zero-latency priority.
    1. URL (Immediate)
    2. Cookie (Immediate)
    3. Redis Cache (Fast - <15ms)
    4. (SKIP) DB lookup is too slow for initial render (approx 1-2s delay)
    """
    # 1. URL Parameter (highest priority)
    fbclid = request.query_params.get('fbclid')
    if fbclid:
        return fbclid
        
    # 2. Cookie (_fbc)
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            return parts[3]
    
    # 3. Redis Cache (L2 Identity)
    try:
        cached = legacy.get_cached_visitor(external_id)
        if cached and cached.get("fbclid"):
            return cached.get("fbclid")
    except Exception as e:
        logger.debug(f"Identity cache miss: {e}")
        
    # 4. 🔥 SKIP DB: For new visitors, we don't block 5 seconds to find a previous ID.
    # The background task 'bg_save_visitor' will eventually link the identity.
    return None

def _schedule_tracking(bt, request, ident, ext_id, fbclid, fbp, event_id):
    if not getattr(request.state, "is_human", True): return
    
    bt.add_task(bg_save_visitor, ext_id, fbclid or "", ident['ip'], ident['ua'], "pageview", {
        'utm_source': request.query_params.get('utm_source'),
        'utm_medium': request.query_params.get('utm_medium'),
        'utm_campaign': request.query_params.get('utm_campaign'),
    }, email=None, phone=None)
    if fbclid:
        bt.add_task(legacy.cache_visitor_data, ext_id, {"fbclid": fbclid})
    
    bt.add_task(bg_send_pageview, str(request.url), ident['ip'], ident['ua'], event_id, fbclid, fbp, ext_id, ident['city'], ident['region'], ident['country'])

def _set_identity_cookies(response, variant, ident, fbclid, fbp):
    response.set_cookie(key="ab_test_group", value=variant, max_age=2592000)
    if not ident.get("is_human", True): return
    
    if not fbp:
        import random
        val = f"fb.1.{int(time.time()*1000)}.{random.randint(100000000, 999999999)}"
        response.set_cookie(key="_fbp", value=val, max_age=31536000, httponly=False, secure=True, samesite="lax")
    
    if fbclid:
        val = f"fb.1.{int(time.time())}.{fbclid}"
        response.set_cookie(key="_fbc", value=val, max_age=31536000, httponly=False, secure=True, samesite="lax")

def _get_feature_flags():
    return {
        "show_testimonials": settings.FLAG_SHOW_TESTIMONIALS,
        "show_gallery": settings.FLAG_SHOW_GALLERY,
        "enable_chat_widget": settings.FLAG_ENABLE_CHAT_WIDGET,
        "cta_variant": settings.FLAG_CTA_VARIANT,
        "hero_style": settings.FLAG_HERO_STYLE,
        "meta_tracking": settings.FLAG_META_TRACKING,
        "maintenance_mode": settings.FLAG_MAINTENANCE_MODE,
        "booking_enabled": settings.FLAG_BOOKING_ENABLED,
    }
