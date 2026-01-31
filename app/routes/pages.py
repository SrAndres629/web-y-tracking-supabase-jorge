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


def bg_send_pageview(event_source_url, client_ip, user_agent, event_id, fbclid, fbp, external_id):
    """Sends PageView to Meta CAPI without blocking"""
    try:
        success = send_event(
            event_name="PageView",
            event_source_url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            event_id=event_id,
            fbclid=fbclid,
            fbp=fbp,
            external_id=external_id,
            custom_data={}
        )
        if success:
            logger.info(f"✅ [BG] PageView sent to Meta CAPI")
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
    event_id = str(int(time.time() * 1000))
    
    # 🛡️ Real IP Extraction (Cloudflare/Render Proxy Support)
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    
    if cf_ip:
        client_ip = cf_ip
    elif forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host
    
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # Capture fbclid from URL (Meta Ads traffic)
    fbclid = request.query_params.get('fbclid')
    
    # Generate external_id
    external_id = generate_external_id(client_ip, user_agent)
    
    # Fallback: Try to recover fbclid from DB if not in URL
    if not fbclid:
        try:
            fbclid = get_visitor_fbclid(external_id)
        except Exception as e:
            logger.warning(f"⚠️ DB Warning: Could not retrieve fbclid: {e}")
            fbclid = None
    
    # Extract fbclid from _fbc cookie if present
    fbp = fbp_cookie
    if not fbclid and fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
    # Set _fbc cookie if we have fbclid
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(
            key="_fbc", 
            value=fbc_value, 
            max_age=90*24*60*60,  # 90 days
            httponly=True, 
            samesite="lax"
        )
    
    # =================================================================
    # BACKGROUND TASKS (Run AFTER response is sent)
    # =================================================================
    
    # 1. Save Visitor to DB
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
    
    # 2. Send PageView to Meta CAPI
    background_tasks.add_task(
        bg_send_pageview,
        event_source_url=current_url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        fbp=fbp,
        external_id=external_id
    )
    
    # 🚀 INSTANT RESPONSE (Background tasks run after this)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": settings.META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or "",
        "services": SERVICES_CONFIG,
        "contact": CONTACT_CONFIG
    })
