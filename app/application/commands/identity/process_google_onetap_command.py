import logging
import time
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProcessGoogleOneTapCommand:
    user_info: Dict[str, Any]
    client_ip: str
    user_agent: str
    referer: Optional[str] = None
    cf_country: Optional[str] = None
    cf_city: Optional[str] = None

class ProcessGoogleOneTapHandler:
    def __init__(
        self,
        external_id_generator: Callable[[str, str], str],
        event_sender: Callable[..., Awaitable[Dict[str, Any]]],
        visitor_saver: Optional[Callable[..., Any]] = None,
    ):
        self._external_id_generator = external_id_generator
        self._event_sender = event_sender
        self._visitor_saver = visitor_saver

    async def handle(self, cmd: ProcessGoogleOneTapCommand) -> Dict[str, Any]:
        try:
            user_info = cmd.user_info
            
            email = user_info.get("email")
            name = user_info.get("name")
            given_name = user_info.get("given_name")
            family_name = user_info.get("family_name")
            picture = user_info.get("picture")
            
            if not email:
                raise ValueError("Email not found in credential")
            
            external_id = self._external_id_generator(cmd.client_ip, cmd.user_agent)
            event_id = f"onetap_{int(time.time() * 1000)}"
            
            # Persist Identity into Visitor record
            if self._visitor_saver:
                self._visitor_saver(
                    external_id=external_id,
                    fbclid=None,
                    client_ip=cmd.client_ip,
                    user_agent=cmd.user_agent,
                    source="google_onetap",
                    utm_data={},
                    email=email
                )

            # Send Lead event to Meta CAPI
            await self._event_sender(
                event_name="Lead",
                event_id=event_id,
                url=cmd.referer or "https://jorgeaguirreflores.com",
                client_ip=cmd.client_ip,
                user_agent=cmd.user_agent,
                external_id=external_id,
                email=email,
                first_name=given_name,
                last_name=family_name,
                city=cmd.cf_city,
                country=cmd.cf_country,
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
            
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"❌ [ONE TAP] Error: {e}")
            return {"status": "error", "message": "Internal error processing Google One Tap credential"}
