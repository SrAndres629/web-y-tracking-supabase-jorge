# =================================================================
# TRACKING_ROUTES.PY - FastAPI Native Background Tasks (Zero Celery)
# Jorge Aguirre Flores Web
# =================================================================
# 
# ARCHITECTURE: "Third Way" Solution
# - No Celery workers required (works on Render free tier)
# - No synchronous blocking (page loads instantly)
# - Uses FastAPI's native BackgroundTasks to process after response
# =================================================================

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Cookie
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import logging

from app.config import settings
from app.models import TrackResponse, LeadCreate, InteractionCreate

# Direct imports (bypassing Celery)
from app.tracking import send_event, send_n8n_webhook
from app.database import save_visitor, upsert_contact_advanced, get_or_create_lead, log_interaction
import app.database as database

# Logger
logger = logging.getLogger("BackgroundWorker")

# Router
router = APIRouter()

# Meta CAPI Configuration
PIXEL_ID = settings.META_PIXEL_ID
ACCESS_TOKEN = settings.META_ACCESS_TOKEN
TEST_EVENT_CODE = settings.TEST_EVENT_CODE


# =================================================================
# 1. MINI-WORKERS (Execute after HTTP response is sent)
# =================================================================

def bg_save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data):
    """Saves visitor to DB without blocking user"""
    try:
        save_visitor(external_id, fbclid, client_ip, user_agent, source, utm_data)
        logger.info(f"✅ [BG] Visitor saved: {external_id[:16]}...")
    except Exception as e:
        logger.error(f"❌ [BG] Error saving visitor: {e}")


def bg_send_meta_event(event_name, event_source_url, client_ip, user_agent, event_id, 
                       fbclid=None, fbp=None, external_id=None, phone=None, email=None, custom_data=None):
    """Sends to Meta CAPI without blocking"""
    try:
        success = send_event(
            event_name=event_name,
            event_source_url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            event_id=event_id,
            fbclid=fbclid,
            fbp=fbp,
            external_id=external_id,
            phone=phone,
            email=email,
            custom_data=custom_data
        )
        if success:
            logger.info(f"✅ [BG] Meta Event sent: {event_name}")
        else:
            logger.warning(f"⚠️ [BG] Meta Event failed (no retry): {event_name}")
    except Exception as e:
        logger.error(f"❌ [BG] Meta send error: {e}")


def bg_upsert_contact(payload):
    """Syncs contact to CRM without blocking"""
    try:
        upsert_contact_advanced(payload)
        logger.info(f"✅ [BG] Contact synced: {payload.get('phone', 'unknown')}")
    except Exception as e:
        logger.error(f"❌ [BG] Contact sync failed: {e}")


def bg_send_webhook(payload):
    """Sends webhook to n8n without blocking"""
    try:
        success = send_n8n_webhook(payload)
        if success:
            logger.info(f"✅ [BG] n8n Webhook sent")
    except Exception as e:
        logger.error(f"⚠️ [BG] Webhook failed: {e}")


# =================================================================
# 2. TRACKING EVENT ENDPOINT (Main)
# =================================================================

class TrackingEvent(BaseModel):
    event_name: str
    event_time: int
    event_id: str
    user_data: Dict[str, Any]
    custom_data: Optional[Dict[str, Any]] = None
    event_source_url: str
    action_source: str = "website"


@router.post("/track/event")
async def track_event(
    event: TrackingEvent, 
    request: Request, 
    background_tasks: BackgroundTasks,
    # Auto-capture _fbp cookie for EMQ boost
    fbp: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc: Optional[str] = Cookie(default=None, alias="_fbc")
):
    """
    Receives frontend events, responds INSTANTLY, processes in background.
    
    The magic: background_tasks.add_task() runs AFTER the HTTP response.
    """
    # 🛡️ ROAS PROTECTION: Real IP Extraction (Cloudflare/Proxy Support)
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    
    if cf_ip:
        client_ip = cf_ip
    elif forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host
        
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Extract Data
    custom_data = event.custom_data or {}
    logger.info(f"📥 Event: {event.event_name} | IP: {client_ip}")
    
    fbclid = custom_data.get('fbclid')
    external_id = event.user_data.get('external_id')
    
    # Inject cookies into custom_data for EMQ boost
    if fbp:
        custom_data['fbp'] = fbp
    if fbc:
        custom_data['fbc'] = fbc
        # Extract fbclid from fbc cookie if not present
        if not fbclid and fbc.startswith("fb.1."):
            parts = fbc.split(".")
            if len(parts) >= 4:
                fbclid = parts[3]

    # Extract UTMs
    utm_data = {
        'utm_source': custom_data.get('utm_source'),
        'utm_medium': custom_data.get('utm_medium'),
        'utm_campaign': custom_data.get('utm_campaign'),
        'utm_term': custom_data.get('utm_term'),
        'utm_content': custom_data.get('utm_content')
    }
    
    # =================================================================
    # BACKGROUND TASK QUEUE (Executes AFTER response is sent)
    # =================================================================
    
    # 1. Save Visitor (Persistence)
    background_tasks.add_task(
        bg_save_visitor,
        external_id=external_id or "anon",
        fbclid=fbclid,
        client_ip=client_ip,
        user_agent=user_agent,
        source=event.event_name,
        utm_data=utm_data
    )

    # 2. Save Lead (If applicable)
    phone = custom_data.get('phone') or event.user_data.get('phone')
    email = custom_data.get('email') or event.user_data.get('email')
    
    if event.event_name == 'Lead' and phone:
        contact_payload = {
            'phone': phone,
            'name': custom_data.get('name') or event.user_data.get('name'),
            'fbclid': fbclid,
            'fbp': fbp,
            'status': 'interested',
            'service_interest': custom_data.get('service_type') or utm_data.get('utm_campaign'),
            **utm_data
        }
        background_tasks.add_task(bg_upsert_contact, contact_payload)

    # 3. Send to Meta CAPI
    background_tasks.add_task(
        bg_send_meta_event,
        event_name=event.event_name,
        event_source_url=event.event_source_url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event.event_id,
        fbclid=fbclid,
        fbp=fbp,
        external_id=external_id,
        phone=phone,
        email=email,
        custom_data=custom_data
    )
    
    # 4. Send to n8n (Important events only)
    IMPORTANT_EVENTS = ['Lead', 'Purchase', 'SliderInteraction']
    if event.event_name in IMPORTANT_EVENTS:
        webhook_payload = event.model_dump()
        webhook_payload['utm_data'] = utm_data
        background_tasks.add_task(bg_send_webhook, webhook_payload)
    
    # 🚀 INSTANT RESPONSE (Background tasks run after this)
    return {
        "status": "queued", 
        "mode": "fastapi_background", 
        "event_id": event.event_id
    }


# =================================================================
# 3. W-003: TRACKING RESCUE ROUTES (Direct DB, no background needed)
# =================================================================

@router.post("/track/lead", response_model=TrackResponse)
async def track_lead_context(request: LeadCreate):
    """
    Endpoint for n8n/webhook.
    Creates or updates a Lead linked to WhatsApp and Meta.
    """
    try:
        data = {
            "meta_lead_id": request.meta_lead_id,
            "click_id": request.click_id,
            "email": request.email,
            "name": request.name
        }
        if request.extra_data:
            data.update(request.extra_data)

        lead_id = database.get_or_create_lead(request.whatsapp_phone, data)
        
        if lead_id:
             return TrackResponse(status="success", event_id=str(lead_id), category="lead_generated")
        else:
             raise HTTPException(status_code=500, detail="Database Error creating Lead")

    except Exception as e:
        logger.error(f"❌ Error in /track/lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/interaction", response_model=TrackResponse)
async def track_interaction(request: InteractionCreate):
    """
    Endpoint for logging messages (User/AI).
    """
    try:
        success = database.log_interaction(request.lead_id, request.role, request.content)
        if success:
            return TrackResponse(status="success", event_id=request.lead_id, category="interaction_logged")
        else:
            raise HTTPException(status_code=500, detail="Database Error logging interaction")
    except Exception as e:
        logger.error(f"❌ Error in /track/interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
