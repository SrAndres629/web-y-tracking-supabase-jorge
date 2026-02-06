# =================================================================
# IDENTITY_ROUTES.PY - Zero-Friction Identity Capture
# Phase 7: Google One Tap + WhatsApp Tracker
# =================================================================

import logging
import time
import uuid
import base64
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response, Query, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.config import settings
from app.tracking import generate_external_id
from app.meta_capi import send_elite_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/identity", tags=["Identity"])


# =================================================================
# MODELS
# =================================================================

class GoogleCredential(BaseModel):
    """Google One Tap credential response"""
    credential: str  # JWT token
    client_id: Optional[str] = None


class WhatsAppLinkRequest(BaseModel):
    """Links phone number to previous session"""
    phone: str
    session_id: str


# =================================================================
# IN-MEMORY SESSION STORE (Use Redis in production)
# =================================================================

_pending_sessions: Dict[str, Dict[str, Any]] = {}


def _store_session(session_id: str, data: Dict[str, Any], ttl: int = 3600):
    """Store session data (replace with Redis for persistence)"""
    data["expires_at"] = time.time() + ttl
    _pending_sessions[session_id] = data
    # Cleanup old sessions
    current_time = time.time()
    expired = [k for k, v in _pending_sessions.items() if v.get("expires_at", 0) < current_time]
    for k in expired:
        del _pending_sessions[k]


def _get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session data"""
    data = _pending_sessions.get(session_id)
    if data and data.get("expires_at", 0) > time.time():
        return data
    return None


# =================================================================
# GOOGLE ONE TAP ENDPOINT
# =================================================================

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
        raise HTTPException(status_code=400, detail="Invalid credential")


@router.post("/google")
async def receive_google_credential(
    request: Request,
    background_tasks: BackgroundTasks,
    body: GoogleCredential
):  # noqa: C901
    """
    Receives Google One Tap credential and extracts user info.
    Sends Lead event to Meta CAPI with verified email.
    """
    try:
        # Decode the JWT to get user info
        user_info = _decode_google_jwt(body.credential)
        
        email = user_info.get("email")
        name = user_info.get("name")
        given_name = user_info.get("given_name")
        family_name = user_info.get("family_name")
        picture = user_info.get("picture")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in credential")
        
        # Extract request context
        forwarded = request.headers.get("x-forwarded-for")
        cf_ip = request.headers.get("cf-connecting-ip")
        client_ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else request.client.host)
        user_agent = request.headers.get("user-agent", "")
        
        external_id = generate_external_id(client_ip, user_agent)
        event_id = f"onetap_{int(time.time() * 1000)}"
        
        # Cloudflare Geo (if available)
        cf_country = request.headers.get("cf-ipcountry")
        cf_city = request.headers.get("cf-ipcity")
        
        # Send Lead event to Meta CAPI
        background_tasks.add_task(
            send_elite_event,
            event_name="Lead",
            event_id=event_id,
            url=str(request.headers.get("referer", "https://jorgeaguirreflores.com")),
            client_ip=client_ip,
            user_agent=user_agent,
            external_id=external_id,
            email=email,
            first_name=given_name,
            last_name=family_name,
            city=cf_city,
            country=cf_country,
            custom_data={"content_name": "google_one_tap", "content_category": "identity"}
        )
        
        logger.info(f"✅ [ONE TAP] Captured: {email[:3]}***@{email.split('@')[1]}")
        
        return {
            "status": "success",
            "message": "Identity captured",
            "user": {
                "email": email,
                "name": name,
                "picture": picture
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ONE TAP] Error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


# =================================================================
# WHATSAPP REDIRECT TRACKER
# =================================================================

@router.get("/whatsapp/redirect")
async def whatsapp_redirect(
    request: Request,
    background_tasks: BackgroundTasks,
    service: Optional[str] = Query(default=None, description="Service interest"),
    source: Optional[str] = Query(default="website", description="Traffic source")
):
    """
    Tracks WhatsApp click intent before redirecting.
    Without external automation (n8n/Evolution), we track the CLICK as the key conversion event.
    """
    # Extract visitor fingerprint
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    client_ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else request.client.host)
    user_agent = request.headers.get("user-agent", "")
    
    external_id = generate_external_id(client_ip, user_agent)
    event_id = f"wa_click_{int(time.time() * 1000)}"
    
    # Cloudflare Geo
    cf_country = request.headers.get("cf-ipcountry")
    cf_city = request.headers.get("cf-ipcity")
    
    # Send Contact event to Meta CAPI (High Value Intent)
    background_tasks.add_task(
        send_elite_event,
        event_name="Contact",
        event_id=event_id,
        url=str(request.headers.get("referer", "https://jorgeaguirreflores.com")),
        client_ip=client_ip,
        user_agent=user_agent,
        external_id=external_id,
        city=cf_city,
        country=cf_country,
        custom_data={
            "content_name": service or "general_inquiry",
            "content_category": "whatsapp_click",
            "lead_source": source
        }
    )
    
    # Build WhatsApp URL with pre-filled message
    message = f"Hola, me interesa información sobre {service or 'sus servicios'}."
    wa_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={message.replace(' ', '%20')}"
    
    logger.info(f"📱 [WA TRACK] Redirecting IP {client_ip} to WhatsApp")
    
    return RedirectResponse(url=wa_url, status_code=302)
