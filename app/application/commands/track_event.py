"""
📊 Track Event Command.

Case of use: Register a tracking event.
Orchestrates deduplication, persistence and sending to external trackers.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from app.application.dto.tracking_dto import (
    TrackEventRequest,
    TrackEventResponse,
    TrackingContext,
)
from app.application.interfaces.cache_port import DeduplicationPort
from app.application.interfaces.tracker_port import TrackerPort
from app.domain.models.events import EventName, TrackingEvent
from app.domain.models.values import ExternalId, UTMParams
from app.domain.repositories.event_repo import EventRepository
from app.domain.repositories.visitor_repo import VisitorRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrackEventCommand:
    """Input for the handler."""

    request: TrackEventRequest
    context: TrackingContext


class TrackEventHandler:
    """
    Handler for tracking events.

    Flow:
    1. Deduplication (fast cache)
    2. Get/create visitor
    3. Create domain event
    4. Persist event
    5. Send to external trackers (async)

    It's idempotent: same event_id = same result.
    """

    def __init__(
        self,
        deduplicator: DeduplicationPort,
        visitor_repo: VisitorRepository,
        event_repo: EventRepository,
        trackers: List[TrackerPort],
    ):
        self.deduplicator = deduplicator
        self.visitor_repo = visitor_repo
        self.event_repo = event_repo
        self.trackers = trackers
        self.tenant_id: str | None = None

    async def handle(self, cmd: TrackEventCommand) -> TrackEventResponse:
        """
        Executes the use case.

        Args:
            cmd: Command with request and context

        Returns:
            TrackEventResponse with result
        """
        try:
            # 1. Parse EventName
            try:
                event_name = EventName(cmd.request.event_name)
            except ValueError:
                return TrackEventResponse.error(f"Invalid event name: {cmd.request.event_name}")

            # 2. Create ExternalId
            external_id_result = ExternalId.from_string(cmd.request.external_id)
            if external_id_result.is_err:
                return TrackEventResponse.error(external_id_result.unwrap_err())
            external_id = external_id_result.unwrap()

            # 3. Check deduplication (fast path)
            event_id_str = f"{cmd.request.event_name}:{external_id.value}:{int(datetime.now(timezone.utc).timestamp() / 3600)}"
            if not await self.deduplicator.is_unique(event_id_str):
                logger.info("🔄 Duplicate event blocked: %s", event_id_str)
                return TrackEventResponse.duplicate(event_id_str)

            # 4. Get or create visitor
            visitor = await self.visitor_repo.get_by_external_id(external_id)
            if not visitor:
                # Create visitor implicitly
                from app.domain.models.visitor import Visitor, VisitorSource

                visitor = Visitor.create(
                    ip=cmd.context.ip_address,
                    user_agent=cmd.context.user_agent,
                    fbclid=cmd.request.fbclid,
                    fbp=cmd.request.fbp,
                    source=VisitorSource.PAGEVIEW,
                    utm=UTMParams.from_dict(
                        {
                            "utm_source": cmd.request.utm_source,
                            "utm_medium": cmd.request.utm_medium,
                            "utm_campaign": cmd.request.utm_campaign,
                            "utm_term": cmd.request.utm_term,
                            "utm_content": cmd.request.utm_content,
                        }
                    ),
                )
                await self.visitor_repo.save(visitor)
            else:
                # Update existing visitor
                visitor.record_visit()
                if cmd.request.fbclid:
                    visitor.update_fbclid(cmd.request.fbclid)
                if cmd.request.fbp:
                    visitor.update_fbp(cmd.request.fbp)
                await self.visitor_repo.update(visitor)

            # 5. Create domain event
            event = TrackingEvent.create(
                event_name=event_name,
                external_id=external_id,
                source_url=cmd.request.source_url,
                custom_data=cmd.request.custom_data,
                utm=UTMParams.from_dict(
                    {
                        "utm_source": cmd.request.utm_source,
                        "utm_medium": cmd.request.utm_medium,
                        "utm_campaign": cmd.request.utm_campaign,
                    }
                ),
            )

            # 6. Persist event
            await self.event_repo.save(event)

            logger.info("✅ Event tracked: %s (%s)", event.event_name.value, event.event_id)

            # 7. Start trackers (no await)
            asyncio.create_task(self._send_to_trackers(event, visitor))

            return TrackEventResponse(
                success=True,
                event_id=event.event_id.value,
                status="queued",
                message=f"{event.event_name.value} tracked successfully",
            )

        except Exception as e:
            logger.exception("❌ Error tracking event")
            return TrackEventResponse.error(str(e))

    async def _send_to_trackers(self, event: TrackingEvent, visitor) -> None:
        """
        Sends event to all configured trackers.

        Does not raise exceptions - errors are logged silently.
        """
        if not self.trackers:
            return

        tasks = []
        for tracker in self.trackers:
            try:
                task = tracker.track(event, visitor)
                tasks.append(task)
            except Exception:
                logger.exception("Failed to create tracking task for %s", tracker.name)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for tracker, result in zip(self.trackers, results, strict=False):
                if isinstance(result, Exception):
                    logger.error("Tracker %s failed: %s", tracker.name, result)
                else:
                    logger.debug("Tracker %s succeeded", tracker.name)
