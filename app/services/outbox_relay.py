"""
📨 Outbox Relay Worker Service
Processes pending state changes exactly once synchronously via CRON.
"""

import json
import logging
from typing import Any, Dict

from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


class OutboxRelay:
    @staticmethod
    async def process_pending_events(batch_size: int = 10) -> int:
        """Processes up to `batch_size` pending events cleanly."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                rows = OutboxRelay._fetch_pending(cur, batch_size)

                if not rows:
                    return 0

                processed = 0
                for row in rows:
                    success = await OutboxRelay._process_single(cur, row)
                    if success:
                        processed += 1

                return processed

        except Exception as e:
            logger.error(f"❌ Relay Worker Error: {e}")
            return 0

    @staticmethod
    def _fetch_pending(cur, batch_size: int) -> list:
        """Pulls pending records from the DB."""
        query = """
            SELECT id, aggregate_type, aggregate_id, event_type, payload 
            FROM outbox_events 
            WHERE status = 'pending' 
            ORDER BY created_at ASC 
            LIMIT %s
        """
        if db.backend == "sqlite":
            query = query.replace("%s", "?")

        cur.execute(query, (batch_size,))
        return cur.fetchall()

    @staticmethod
    def _mark_status(cur, event_id: str, status: str, error_msg: str = None):
        """Standardizes status updates for the relay lock."""
        if status == "processing":
            query = "UPDATE outbox_events SET status = 'processing' WHERE id = %s"
            params = (event_id,)
        elif status == "completed":
            query = "UPDATE outbox_events SET status = 'completed', processed_at = CURRENT_TIMESTAMP WHERE id = %s"
            params = (event_id,)
        else:
            query = "UPDATE outbox_events SET status = 'failed', error_msg = %s WHERE id = %s"
            params = (error_msg, event_id)

        if db.backend == "sqlite":
            query = query.replace("%s", "?")

        cur.execute(query, params)

    @staticmethod
    async def _process_single(cur, row: tuple) -> bool:
        """Processes a single extracted log."""
        event_id = row[0]
        agg_type = row[1]
        event_type = row[3]
        payload_json = row[4]

        try:
            OutboxRelay._mark_status(cur, event_id, "processing")

            payload = (
                json.loads(payload_json)
                if isinstance(payload_json, str)
                else payload_json
            )
            await OutboxRelay._handle_event(agg_type, event_type, payload)

            OutboxRelay._mark_status(cur, event_id, "completed")
            return True
        except Exception as e:
            logger.error(f"❌ Relay processing failed for {event_id}: {e}")
            OutboxRelay._mark_status(cur, event_id, "failed", str(e))
            return False

    @staticmethod
    async def _handle_event(agg_type: str, event_type: str, payload: Dict[str, Any]):
        """Dispatches the event to the correct handler (Meta CAPI Circuit-Breaker wrapped)"""
        if event_type not in ["TRACKING_EVENT_SAVED", "LEAD_SAVED"]:
            return

        from app.infrastructure.external.meta_capi.tracker import MetaTracker

        tracker = MetaTracker()

        if agg_type == "TrackingEvent":
            await OutboxRelay._handle_tracking_event(tracker, payload)
        elif agg_type == "Lead":
            await OutboxRelay._handle_lead_event(tracker, payload)

    @staticmethod
    async def _handle_tracking_event(tracker, payload: Dict[str, Any]):
        custom_data = payload.get("custom_data", {})
        fbp = custom_data.get("fbp")
        fbc = custom_data.get("fbc") or custom_data.get("fbclid")

        if fbc and not fbc.startswith("fb."):
            import time

            fbc = f"fb.1.{int(time.time())}.{fbc}"

        await tracker.track(
            event_name=payload.get("event_name"),
            event_id=payload.get("event_id"),
            url=payload.get("source_url", "https://jorgeaguirreflores.com"),
            client_ip=custom_data.get("client_ip", "127.0.0.1"),
            user_agent=custom_data.get("user_agent", "OutboxRelay/1.0"),
            external_id=payload.get("external_id"),
            fbp=fbp,
            fbc=fbc,
            custom_data=custom_data,
        )

    @staticmethod
    async def _handle_lead_event(tracker, payload: Dict[str, Any]):
        await tracker.track(
            event_name="Lead",
            event_id=payload.get("id"),
            url="https://jorgeaguirreflores.com",
            client_ip="127.0.0.1",
            user_agent="OutboxRelay/1.0",
            phone=payload.get("phone"),
            email=payload.get("email"),
            custom_data={
                "status": payload.get("status"),
                "score": payload.get("score"),
            },
        )
