import asyncio
import os
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from app.application.commands.track_event import TrackEventHandler, TrackEventCommand
from app.application.dto.tracking_dto import TrackEventRequest, TrackingContext
from app.application.interfaces.cache_port import DeduplicationPort
from app.domain.models.values import ExternalId
from app.domain.repositories.visitor_repo import VisitorRepository
from app.domain.repositories.event_repo import EventRepository
from app.tracking import TinybirdTracker

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Mocks ---

class MockDeduplicator(DeduplicationPort):
    async def is_unique(self, event_key: str) -> bool:
        return True
    async def mark_processed(self, event_key: str, ttl_seconds: int = 86400) -> None:
        pass

class MockVisitorRepo(VisitorRepository):
    async def get_by_external_id(self, external_id):
        return None
    async def get_by_fbclid(self, fbclid: str):
        return None
    async def save(self, visitor: Any) -> None:
        pass
    async def create(self, visitor: Any) -> None:
        pass
    async def update(self, visitor: Any) -> None:
        pass
    async def list_recent(self, limit: int = 50, offset: int = 0) -> List[Any]:
        return []
    async def count(self) -> int:
        return 0
    async def exists(self, external_id: Any) -> bool:
        return False

class MockEventRepo(EventRepository):
    async def save(self, event: Any) -> None:
        pass
    async def get_by_id(self, event_id: Any):
        return None
    async def list_by_visitor(self, external_id: Any, limit: int = 100) -> List[Any]:
        return []
    async def list_by_visitor_and_type(self, external_id: Any, event_name: Any, limit: int = 50) -> List[Any]:
        return []
    async def list_by_date_range(self, start: Any, end: Any, event_name: Any = None, limit: int = 1000) -> List[Any]:
        return []
    async def exists(self, event_id: Any) -> bool:
        return False
    async def count_by_visitor(self, external_id: Any) -> int:
        return 0
    async def count_by_type_and_date(self, event_name: Any, date: Any) -> int:
        return 0

# --- Test Execution ---

async def verify_pipeline():
    print("🚀 Starting TinybirdTracker Integration Test...")
    
    # 1. Setup Tracker
    tracker = TinybirdTracker()
    if not tracker._enabled:
        print("❌ TinybirdTracker is disabled (missing token)")
        return

    # 2. Setup Handler
    handler = TrackEventHandler(
        deduplicator=MockDeduplicator(),
        visitor_repo=MockVisitorRepo(),
        event_repo=MockEventRepo(),
        trackers=[tracker]
    )

    # 3. Create Sample Request
    request = TrackEventRequest(
        event_name="Lead",
        external_id="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",  # 32 chars hex
        source_url="https://jorgeaguirreflores.com/test",
        custom_data={"test_mode": True, "source": "integration_test"},
        fbclid="test_fbclid_456"
    )
    
    context = TrackingContext(
        ip_address="127.0.0.1",
        user_agent="Antigravity Integration Test Client"
    )
    
    command = TrackEventCommand(request=request, context=context)

    # 4. Handle Event
    print("💎 Sending Lead event through pipeline...")
    response = await handler.handle(command)
    
    if response.success:
        print(f"✅ Handler report success! Event ID: {response.event_id}")
    else:
        print(f"❌ Handler failed: {response.message}")

    # Allow some time for the background task to complete
    print("⏳ Waiting for Tinybird background task...")
    await asyncio.sleep(2)
    print("🏁 Test finished. Check logs above for '[TINYBIRD] ✅ Event Lead streamed successfully'")

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
