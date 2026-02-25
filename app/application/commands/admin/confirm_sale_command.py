import time
from typing import Any, Awaitable, Callable, Dict, Optional

from app.infrastructure.config.settings import settings


from app.domain.models.visitor import Visitor

class ConfirmSaleCommand:
    def __init__(
        self,
        get_visitor_by_id: Callable[[str], Awaitable[Optional[Visitor]]],
        event_sender: Callable[..., Awaitable[None]],
    ):
        self._get_visitor_by_id = get_visitor_by_id
        self._event_sender = event_sender

    async def execute(
        self,
        visitor_id: str,
        client_ip: str,
        user_agent: str,
        fbclid: Optional[str] = None,
        fbp: Optional[str] = None,
        fbc: Optional[str] = None,
        external_id: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Confirms a sale and sends a Purchase event to Meta CAPI.
        """
        visitor = await self._get_visitor_by_id(visitor_id)
        if not visitor:
            return {"status": "error", "error": f"Visitor {visitor_id} not found"}

        # Prepare custom_data with default values if not provided
        if custom_data is None:
            custom_data = {"value": 350.00, "currency": "USD"}
        else:
            # Ensure default values are present if not explicitly overridden
            custom_data.setdefault("value", 350.00)
            custom_data.setdefault("currency", "USD")

        # Send Purchase event to Meta CAPI
        try:
            # Use data from visitor domain model
            v_external_id = str(visitor.external_id)
            v_fbclid = visitor.fbclid or fbclid
            v_fbp = visitor.fbp or fbp
            v_email = visitor.email.value if visitor.email else None
            v_phone = visitor.phone.value if visitor.phone else None

            from app.domain.models.events import TrackingEvent, EventName
            from app.domain.models.values import EventId, ExternalId
            
            event = TrackingEvent(
                event_name=EventName.PURCHASE,
                event_id=EventId(f"purchase_{visitor_id}_{int(time.time())}"),
                external_id=ExternalId(v_external_id),
                source_url=f"{settings.HOST}/admin/confirm",
                custom_data=custom_data,
            )

            # We pass the event to the sender (EventRepository.save)
            await self._event_sender(event)
            
            return {
                "status": "success",
                "visitor_id": visitor_id,
                "message": "Purchase event queued successfully",
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to send Meta CAPI event: {e!s}"}
