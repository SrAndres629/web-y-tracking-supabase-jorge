"""
📊 TrackingEvent Entity - Tracking Event.

Represents a user action we want to track:
- PageView: View page
- ViewContent: View specific service
- Lead: Click WhatsApp, form
- Contact: Contact initiated
- etc.

Immutable (frozen) because historical events do not change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from typing import Any, Optional

    from typing_extensions import Self
except ImportError:
    from typing import Any, Optional

    from typing_extensions import Self

from enum import Enum

from app.domain.models.values import EventId, ExternalId, UTMParams


class EventName(Enum):
    """Supported standard events."""

    PAGE_VIEW = "PageView"
    VIEW_CONTENT = "ViewContent"
    LEAD = "Lead"
    CONTACT = "Contact"
    INITIATE_CHECKOUT = "InitiateCheckout"
    PURCHASE = "Purchase"
    COMPLETE_REGISTRATION = "CompleteRegistration"
    SCHEDULE = "Schedule"
    CUSTOMIZE_PRODUCT = "CustomizeProduct"

    # Custom events
    SLIDER_INTERACTION = "SliderInteraction"
    WHATSAPP_CLICK = "WhatsAppClick"


@dataclass(frozen=True, slots=True)
class TrackingEvent:
    """
    Value Object: Immutable tracking event.

    Events are immutable because they represent something
    that occurred at a specific moment in time.

    Attributes:
        event_id: Unique event ID
        event_name: Type of event
        external_id: Visitor ID
        timestamp: When it occurred
        source_url: URL where it occurred
        custom_data: Event specific data
        utm: UTM parameters (snapshot at event time)
    """

    event_id: EventId
    event_name: EventName
    external_id: ExternalId
    timestamp: datetime
    source_url: str
    custom_data: dict[str, Any] = field(default_factory=dict)
    utm: UTMParams = field(default_factory=UTMParams)

    @classmethod
    def create(
        cls,
        event_name: EventName,
        external_id: ExternalId,
        source_url: str,
        custom_data: Optional[dict[str, Any]] = None,
        utm: Optional[UTMParams] = None,
    ) -> Self:
        """Factory for creating a new event."""
        return cls(
            event_id=EventId.generate(),
            event_name=event_name,
            external_id=external_id,
            timestamp=datetime.now(timezone.utc),
            source_url=source_url,
            custom_data=custom_data or {},
            utm=utm or UTMParams(),
        )

    @classmethod
    def reconstruct(
        cls,
        event_id: EventId,
        event_name: EventName,
        external_id: ExternalId,
        timestamp: datetime,
        source_url: str,
        custom_data: Optional[dict[str, Any]] = None,
        utm: Optional[UTMParams] = None,
    ) -> Self:
        """Reconstructs event from persisted data."""
        return cls(
            event_id=event_id,
            event_name=event_name,
            external_id=external_id,
            timestamp=timestamp,
            source_url=source_url,
            custom_data=custom_data or {},
            utm=utm or UTMParams(),
        )

    def with_custom_data(self, **kwargs: Any) -> TrackingEvent:
        """Returns new event with additional data (immutable)."""
        new_data = {**self.custom_data, **kwargs}
        return TrackingEvent(
            event_id=self.event_id,
            event_name=self.event_name,
            external_id=self.external_id,
            timestamp=self.timestamp,
            source_url=self.source_url,
            custom_data=new_data,
            utm=self.utm,
        )

    def to_meta_payload(self, visitor) -> dict[str, Any]:
        """
        Converts to payload for Meta CAPI.

        Args:
            visitor: Visitor object with additional data
        """
        from app.core.validators import hash_sha256

        payload = {
            "event_name": self.event_name.value,
            "event_time": int(self.timestamp.timestamp()),
            "event_id": self.event_id.value,
            "event_source_url": self.source_url,
            "action_source": "website",
            "user_data": (
                visitor.to_meta_user_data()
                if visitor
                else {
                    "external_id": hash_sha256(self.external_id.value),
                }
            ),
        }

        if self.custom_data:
            payload["custom_data"] = self.custom_data

        return payload

    def is_duplicate_of(self, other: TrackingEvent) -> bool:
        """True if duplicate (same ID)."""
        return self.event_id.value == other.event_id.value

    @property
    def is_conversion_event(self) -> bool:
        """True if conversion event (Lead, Purchase, etc)."""
        return self.event_name in [
            EventName.LEAD,
            EventName.CONTACT,
            EventName.PURCHASE,
            EventName.SCHEDULE,
        ]

    def __repr__(self) -> str:
        return f"TrackingEvent({self.event_name.value}, {self.event_id})"
