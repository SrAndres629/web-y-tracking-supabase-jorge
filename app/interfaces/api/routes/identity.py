import base64
import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.application.commands.identity.process_google_onetap_command import (
    ProcessGoogleOneTapCommand,
    ProcessGoogleOneTapHandler,
)
from app.application.commands.identity.track_whatsapp_redirect_command import (
    TrackWhatsAppRedirectCommand,
    TrackWhatsAppRedirectHandler,
)
from app.interfaces.api.dependencies import get_legacy_facade

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/identity", tags=["Identity"])
legacy = get_legacy_facade()

# =================================================================
# MODELS
# =================================================================


class GoogleCredential(BaseModel):
    """Google One Tap credential response"""

    credential: str  # JWT token
    client_id: Optional[str] = None


def _decode_google_jwt(token: str) -> Dict[str, Any]:
    """
    Decode Google JWT without verification (frontend already verified).
    In production, verify with Google's public keys.
    """
    try:
        # JWT = header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"❌ JWT decode error: {e}")
        raise ValueError("Invalid credential")


# =================================================================
# GOOGLE ONE TAP ENDPOINT
# =================================================================


@router.post("/google")
async def receive_google_credential(
    request: Request, background_tasks: BackgroundTasks, body: GoogleCredential
):
    try:
        user_info = _decode_google_jwt(body.credential)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error decoding credential")

    client_ip = (
        request.headers.get("cf-connecting-ip")
        or (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
        or request.client.host
    )
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")
    cf_country = request.headers.get("cf-ipcountry")
    cf_city = request.headers.get("cf-ipcity")

    command = ProcessGoogleOneTapCommand(
        user_info=user_info,
        client_ip=client_ip,
        user_agent=user_agent,
        referer=referer,
        cf_country=cf_country,
        cf_city=cf_city,
    )

    handler = ProcessGoogleOneTapHandler(
        external_id_generator=legacy.generate_external_id,
        event_sender=legacy.send_elite_event,
        visitor_saver=legacy.save_visitor,
    )

    # Execute the command in a background task
    background_tasks.add_task(handler.handle, command)

    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    return {
        "status": "success",
        "message": "Identity capture initiated",
        "user": {"email": email, "name": name, "picture": picture},
    }


# =================================================================
# WHATSAPP REDIRECT TRACKER
# =================================================================


@router.get("/whatsapp/redirect")
async def whatsapp_redirect(
    request: Request,
    background_tasks: BackgroundTasks,
    service: Optional[str] = Query(default=None, description="Service interest"),
    source: Optional[str] = Query(default="website", description="Traffic source"),
):
    client_ip = (
        request.headers.get("cf-connecting-ip")
        or (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
        or request.client.host
    )
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")
    cf_country = request.headers.get("cf-ipcountry")
    cf_city = request.headers.get("cf-ipcity")

    command = TrackWhatsAppRedirectCommand(
        client_ip=client_ip,
        user_agent=user_agent,
        referer=referer,
        cf_country=cf_country,
        cf_city=cf_city,
        service=service,
        source=source,
    )

    handler = TrackWhatsAppRedirectHandler(
        external_id_generator=legacy.generate_external_id,
        event_sender=legacy.send_elite_event,
    )

    # Execute the command to get the WhatsApp URL, and send the tracking event in background
    # The handler's handle method now returns the URL. The event sending is part of that handle.
    wa_url = await handler.handle(
        command
    )  # This executes the tracking event in background internally.

    logger.info(f"📱 [WA TRACK] Redirecting IP {client_ip} to WhatsApp")

    return RedirectResponse(url=wa_url, status_code=302)
