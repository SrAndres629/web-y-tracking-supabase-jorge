import time
from typing import Dict, Any, Optional, Callable, Awaitable

from app.config import settings

class ConfirmSaleCommand:
    def __init__(
        self,
        get_visitor_by_id: Callable[[int], Optional[Dict[str, Any]]],
        event_sender: Callable[..., Awaitable[Dict[str, Any]]],
    ):
        self._get_visitor_by_id = get_visitor_by_id
        self._event_sender = event_sender

    async def execute(
        self,
        visitor_id: int,
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
        visitor = self._get_visitor_by_id(visitor_id)
        if not visitor:
            return {"status": "error", "error": "Visitor not found"}

        # Prepare custom_data with default values if not provided
        if custom_data is None:
            custom_data = {
                "value": 350.00,
                "currency": "USD"
            }
        else:
            # Ensure default values are present if not explicitly overridden
            custom_data.setdefault("value", 350.00)
            custom_data.setdefault("currency", "USD")

        # Send Purchase event to Meta CAPI
        try:
            await self._event_sender(
                event_name="Purchase",
                event_id=f"purchase_{visitor_id}_{int(time.time())}",
                url=f"{settings.HOST}/admin", # Event source URL, could be more specific
                client_ip=client_ip,
                user_agent=user_agent,
                external_id=visitor.get("external_id") or external_id,
                fbc=visitor.get("fbc") or fbc,
                fbp=visitor.get("fbp") or fbp,
                custom_data=custom_data,
            )
            return {
                "status": "success",
                "visitor_id": visitor_id,
                "message": "Purchase event queued successfully"
            }
        except Exception as e:
            # In a real scenario, proper logging would be implemented here.
            return {"status": "error", "error": f"Failed to send Meta CAPI event: {str(e)}"}
