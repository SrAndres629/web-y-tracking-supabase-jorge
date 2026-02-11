import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.config import settings
from app.tracking import generate_external_id
from app.meta_capi import send_elite_event

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class TrackWhatsAppRedirectCommand:
    client_ip: str
    user_agent: str
    referer: Optional[str] = None
    cf_country: Optional[str] = None
    cf_city: Optional[str] = None
    service: Optional[str] = None
    source: Optional[str] = "website"

class TrackWhatsAppRedirectHandler:
    def __init__(self):
        pass # No external dependencies for this handler beyond those in meta_capi and tracking

    async def handle(self, cmd: TrackWhatsAppRedirectCommand) -> str:
        """
        Tracks a WhatsApp click intent and returns the WhatsApp redirect URL.
        """
        external_id = generate_external_id(cmd.client_ip, cmd.user_agent)
        event_id = f"wa_click_{int(time.time() * 1000)}"
        
        # Send Contact event to Meta CAPI (High Value Intent)
        await send_elite_event(
            event_name="Contact",
            event_id=event_id,
            url=cmd.referer or "https://jorgeaguirreflores.com",
            client_ip=cmd.client_ip,
            user_agent=cmd.user_agent,
            external_id=external_id,
            city=cmd.cf_city,
            country=cmd.cf_country,
            custom_data={
                "content_name": cmd.service or "general_inquiry",
                "content_category": "whatsapp_click",
                "lead_source": cmd.source
            }
        )
        
        # Build WhatsApp URL with pre-filled message
        message = f"Hola, me interesa información sobre {cmd.service or 'sus servicios'}."
        wa_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={message.replace(' ', '%20')}"
        
        logger.info(f"📱 [WA TRACK] Redirecting IP {cmd.client_ip} to WhatsApp")
        
        return wa_url
