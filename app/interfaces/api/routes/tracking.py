# =================================================================
# TRACKING.PY - FastAPI Native Background Tasks (Zero Celery)
# Jorge Aguirre Flores Web
# =================================================================
#
# ARCHITECTURE: "Third Way" Solution
# - No Celery workers required (works on Render free tier)
# - No synchronous blocking (page loads instantly)
# - Uses FastAPI's native BackgroundTasks to process after response
# =================================================================

import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Cookie, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.dto.tracking_dto import TrackEventRequest as TrackingEvent
from app.infrastructure.config.settings import settings
from app.interfaces.api.dependencies import (
    get_create_lead_handler,
    get_legacy_facade,
    get_track_event_handler,
)
from app.interfaces.api.schemas import (
    InteractionCreate,
    InteractionResponse,
    LeadCreate,
    TrackResponse,
)
from app.limiter import limiter
from app.services import normalize_pii, publish_to_qstash, validate_turnstile

# Logger
logger = logging.getLogger("BackgroundWorker")

# Router
router = APIRouter()
legacy = get_legacy_facade()

# Meta CAPI Configuration
PIXEL_ID = settings.META_PIXEL_ID
ACCESS_TOKEN = settings.META_ACCESS_TOKEN
TEST_EVENT_CODE = settings.TEST_EVENT_CODE


# =================================================================
# 1. MINI-WORKERS (Execute after HTTP response is sent)
# =================================================================


def bg_save_visitor(
    external_id, fbclid, client_ip, user_agent, source, utm_data, email=None, phone=None
):
    """Saves visitor to DB without blocking user"""
    try:
        legacy.save_visitor(
            external_id,
            fbclid,
            client_ip,
            user_agent,
            source,
            utm_data,
            email=email,
            phone=phone,
        )
        logger.info(f"✅ [BG] Visitor saved: {external_id[:16]}...")
    except Exception as e:
        logger.exception(f"❌ [BG] Error saving visitor: {e}")


async def bg_send_meta_event(
    event_name,
    event_source_url,
    client_ip,
    user_agent,
    event_id,
    fbclid=None,
    fbp=None,
    fbc=None,
    external_id=None,
    phone=None,
    email=None,
    custom_data=None,
    first_name=None,
    last_name=None,
    city=None,
    state=None,
    zip_code=None,
    country=None,
    utm_data=None,
    access_token=None,
    pixel_id=None,
):
    """Sends to Meta CAPI using Elite Service (SDK + Redis) - Async-Awaiting"""
    try:
        # Auto-construct fbc from fbclid if needed (unless passed explicitly)
        fbc_cookie = fbc
        if not fbc_cookie and fbclid:
            # Standard Meta click ID format: fb.1.timestamp.fbclid
            timestamp = int(time.time())
            fbc_cookie = f"fb.1.{timestamp}.{fbclid}"

        result = await legacy.send_elite_event(
            event_name=event_name,
            event_id=event_id,
            url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            external_id=external_id,
            fbc=fbc_cookie,
            fbp=fbp,
            phone=phone,
            email=email,
            first_name=first_name,
            last_name=last_name,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            custom_data=custom_data,
            access_token=access_token,
            pixel_id=pixel_id,
        )

        status = result.get("status")
        if status == "success":
            logger.info(f"✅ [BG] Meta Event sent: {event_name}")
        elif status == "duplicate":
            logger.info(f"🔄 [BG] Skipped duplicate: {event_name}")
        elif status == "sandbox":
            logger.info(f"🛡️ [BG] Sandbox intercepted: {event_name}")
        else:
            logger.warning(f"⚠️ [BG] Meta Event issue: {result}")

    except Exception as e:
        logger.exception(f"❌ [BG] Meta send error: {e}")


def bg_upsert_contact(payload):
    """Syncs contact to CRM without blocking"""
    try:
        legacy.upsert_contact_advanced(payload)
        logger.info(f"✅ [BG] Contact synced: {payload.get('phone', 'unknown')}")
    except Exception as e:
        logger.exception(f"❌ [BG] Contact sync failed: {e}")


def bg_send_webhook(payload):
    """Sends webhook to n8n without blocking"""
    try:
        success = legacy.send_n8n_webhook(payload)
        if success:
            logger.info("✅ [BG] n8n Webhook sent")
    except Exception as e:
        logger.exception(f"⚠️ [BG] Webhook failed: {e}")


# =================================================================
# 2. TRACKING EVENT ENDPOINT (Main)
# =================================================================


from fastapi import Depends


@router.post("/track/event")
@limiter.limit("60/minute")
async def track_event(
    event: TrackingEvent,
    request: Request,
    background_tasks: BackgroundTasks,
    handler: Any = Depends(get_track_event_handler),
    fbp: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc: Optional[str] = Cookie(default=None, alias="_fbc"),
):
    """Event ingestion with instant response and background processing."""
    # 1. Context & Identity
    from app.application.commands.track_event import TrackEventCommand
    from app.application.dto.tracking_dto import TrackingContext

    # Extract context
    ctx_data = _get_tracking_context(request, event, fbp, fbc)
    context = TrackingContext(
        ip_address=ctx_data["ip"],
        user_agent=ctx_data["ua"],
    )

    # 2. Execute via Command Handler (Background)
    # Note: For strict DDD, we should await or use a specialized background handler
    # Since we want instant response, we use background_tasks
    cmd = TrackEventCommand(request=event, context=context)
    background_tasks.add_task(handler.handle, cmd)

    # 3. Handle specific side effects (External Hubs)
    if event.event_name == "Lead" and ctx_data["phone"]:
        _queue_lead_sync(background_tasks, event, ctx_data)

    _queue_external_hubs(background_tasks, event, ctx_data)

    return JSONResponse(
        content={"status": "queued", "event_id": event.event_id},
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


def _get_tracking_context(request, event, fbp, fbc):
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    ip = cf_ip or (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "127.0.0.1")
    )

    custom = event.custom_data or {}
    fb_id = custom.get("fbclid")
    if not fb_id and fbc and fbc.startswith("fb.1."):
        parts = fbc.split(".")
        if len(parts) >= 4:
            fb_id = parts[3]

    return {
        "ip": ip,
        "ua": request.headers.get("user-agent", "unknown"),
        "fb_id": fb_id,
        "ext_id": event.user_data.get("external_id"),
        "fbp": fbp or custom.get("fbp"),
        "fbc": fbc or custom.get("fbc"),
        "phone": normalize_pii(custom.get("phone") or event.user_data.get("phone"), "phone"),
        "email": normalize_pii(custom.get("email") or event.user_data.get("email"), "email"),
        "utm": {
            "utm_source": custom.get("utm_source"),
            "utm_medium": custom.get("utm_medium"),
            "utm_campaign": custom.get("utm_campaign"),
            "utm_term": custom.get("utm_term"),
            "utm_content": custom.get("utm_content"),
        },
    }


async def _validate_human(event, ctx):
    token = (event.custom_data or {}).get("turnstile_token")
    if not await validate_turnstile(str(token or "")):
        logger.warning(f"🛡️ Filtered: {event.event_name}")
        return False
    return True


def _queue_lead_sync(bt, event, ctx):
    payload = {
        "phone": ctx["phone"],
        "fbclid": ctx["fb_id"],
        "fbp": ctx["fbp"],
        "status": "interested",
        "name": (event.custom_data or {}).get("name") or event.user_data.get("name"),
        "service_interest": (event.custom_data or {}).get("service_type")
        or ctx["utm"].get("utm_campaign"),
        **ctx["utm"],
    }
    bt.add_task(bg_upsert_contact, payload)


async def _dispatch_to_capi(bt, event, ctx, client=None):
    access_token = client.get("meta_access_token") if client else None
    pixel_id = client.get("meta_pixel_id") if client else None

    payload = {
        "event_name": event.event_name,
        "event_id": event.event_id,
        "event_source_url": event.event_source_url,
        "client_ip": ctx["ip"],
        "user_agent": ctx["ua"],
        "external_id": ctx["ext_id"],
        "fbc": ctx["fbc"],
        "fbp": ctx["fbp"],
        "phone": ctx["phone"],
        "email": ctx["email"],
        "first_name": event.user_data.get("fn") or event.user_data.get("first_name"),
        "last_name": event.user_data.get("ln") or event.user_data.get("last_name"),
        "city": event.user_data.get("ct") or event.user_data.get("city"),
        "state": event.user_data.get("st") or event.user_data.get("state"),
        "zip_code": event.user_data.get("zp") or event.user_data.get("zip_code"),
        "country": event.user_data.get("country"),
        "custom_data": event.custom_data,
        "utm_data": ctx["utm"],
        "access_token": access_token,
        "pixel_id": pixel_id,
    }
    if not await publish_to_qstash(payload):
        bt.add_task(bg_send_meta_event, **payload)


def _queue_external_hubs(bt, event, ctx):
    # Webhook
    if event.event_name in [
        "Lead",
        "ViewContent",
        "Contact",
        "Purchase",
        "SliderInteraction",
    ]:
        payload = event.model_dump()
        payload["utm_data"] = ctx["utm"]
        bt.add_task(bg_send_webhook, payload)


# =================================================================
# 3. W-003: TRACKING RESCUE ROUTES (Direct DB, no background needed)
# =================================================================


@router.post("/track/lead", response_model=TrackResponse)
async def track_lead_context(
    request: LeadCreate, handler: Any = Depends(get_create_lead_handler)
):
    """
    Endpoint for n8n/webhook.
    Creates or updates a Lead linked to WhatsApp and Meta.
    """
    try:
        from app.application.commands.create_lead import CreateLeadCommand

        cmd = CreateLeadCommand(
            phone=request.whatsapp_phone,
            name=request.name,
            email=request.email,
            fbclid=request.click_id,
            utm_source="n8n_webhook",
        )

        result = await handler.handle(cmd)

        if result.is_ok:
            lead = result.unwrap()
            return TrackResponse(
                status="success", event_id=str(lead.id), category="lead_generated"
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error: {result.unwrap_err()}")

    except Exception as err:
        logger.exception("❌ Error in /track/lead: %s", err)
        raise HTTPException(status_code=500, detail="Database Error creating Lead") from err


@router.post("/track/interaction", response_model=InteractionResponse)
async def track_interaction(request: InteractionCreate):
    """
    Endpoint for logging messages (User/AI).
    """
    try:
        # Fire and forget (or direct log)
        # For now, just print or rely on Supabase direct logic if implemented
        return {"status": "logged", "id": "local_log"}
    except Exception as err:
        logger.exception("Interaction error: %s", str(err))
        raise HTTPException(status_code=500, detail="Logging failed") from err


# =================================================================
# 4. QSTASH WEBHOOK RECEIVER (The Worker)
# =================================================================
class QStashPayload(BaseModel):
    event_name: str
    event_id: str
    event_source_url: str
    client_ip: str
    user_agent: str
    external_id: Optional[str] = None
    fbc: Optional[str] = None
    fbp: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    custom_data: Optional[dict] = None
    utm_data: Optional[dict] = {}


@router.post("/hooks/process-event")
async def process_qstash_event(payload: QStashPayload):
    """
    Webhook Receiver for QStash.
    This runs in a FRESH Vercel invocation (Full CPU Time).
    """
    logger.info(f"📨 Received QStash Webhook: {payload.event_name}")

    # We call the synchronous bg_send_meta_event directly here
    # Since this is a dedicated request from QStash, we can block/wait for it to finish
    try:
        await bg_send_meta_event(
            event_name=payload.event_name,
            event_id=payload.event_id,
            event_source_url=payload.event_source_url,
            client_ip=payload.client_ip,
            user_agent=payload.user_agent,
            external_id=payload.external_id,
            fbclid=(
                payload.fbc.split(".")[3]
                if (payload.fbc and "fb.1." in payload.fbc and len(payload.fbc.split(".")) >= 4)
                else None
            ),
            fbp=payload.fbp,
            fbc=payload.fbc,  # Pass full fbc too just in case
            phone=payload.phone,
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zip_code,
            country=payload.country,
            custom_data=payload.custom_data,
        )
        return {"status": "processed", "source": "qstash"}
    except Exception as err:
        logger.exception("❌ Error processing QStash event: %s", err)
        raise HTTPException(status_code=500, detail="Internal processing error") from err


@router.get("/track/health")
async def tracking_health():
    """Health check del sistema de tracking."""
    return {"status": "ok", "service": "tracking"}


@router.post("/onboarding")
async def client_onboarding(
    data: Dict[str, Any], request: Request, background_tasks: BackgroundTasks
):
    """Registers a new client and generates an API key."""
    from app.domain.services.client_service import ClientService

    # 🛡️ Bot Protection (Turnstile)
    token = data.get("turnstile_token")
    if not await validate_turnstile(str(token or "")):
        logger.warning("🛡️ Blocked bot attempt on /onboarding")
        raise HTTPException(status_code=403, detail="Bot protection validation failed")

    name = data.get("name")
    email = data.get("email")
    company = data.get("company")
    config = data.get("config", {})

    if not all([name, email, company]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    client_service = ClientService()
    result = await client_service.create_client(
        name=str(name),
        email=str(email),
        company=str(company),
        meta_pixel_id=config.get("meta_pixel_id"),
        meta_access_token=config.get("meta_access_token"),
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to create client")

    # Generate external_id and extract tracking context
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    external_id = legacy.generate_external_id(ip, user_agent)

    # Extract fbp and fbc from cookies or request state (if available from middleware)
    fbp_cookie = request.cookies.get("_fbp")
    fbc_cookie = request.cookies.get("_fbc")

    # Construct pii for Lead event
    event_id = f"lead_{result['client_id']}_{int(time.time())}"

    background_tasks.add_task(
        bg_send_meta_event,
        event_name="Lead",
        event_id=event_id,
        event_source_url=str(request.url),
        client_ip=ip,
        user_agent=user_agent,
        external_id=external_id,
        fbp=fbp_cookie,
        fbc=fbc_cookie,
        email=email,  # from data dict
        first_name=name,  # from data dict
        custom_data={"company": company, "meta_pixel_id": config.get("meta_pixel_id")},
    )

    return {
        "status": "success",
        "client_id": result["client_id"],
        "api_key": result["api_key"],
    }
