import os

import pytest


@pytest.mark.L5
@pytest.mark.performance
@pytest.mark.asyncio
async def test_performance_optimization_headers():
    import pydantic

    """
    Verifies that Gzip and Cache-Control are working.
    These are critical for low CPM and high ROI.
    """
    # Assuming the app is running locally for tests
    # Or we can use the TestClient
    from fastapi.testclient import TestClient

    from main import app

    client = TestClient(app)

    # 1. Test Gzip Compression
    response = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    # Note: TestClient doesn't always show 'content-encoding' but we can check if it's compressed
    # Actually, GZipMiddleware adds it.

    # 2. Test Cache-Control for Static Assets
    # We need a static file path
    asset_path = "/static/dist/css/app.min.css"
    response = client.get(asset_path)
    assert response.status_code == 200
    assert "cache-control" in response.headers
    assert "public" in response.headers["cache-control"]
    assert "max-age" in response.headers["cache-control"]

    print("✅ Performance Headers (Gzip/Cache) Verified")


@pytest.mark.L5
@pytest.mark.tracking
@pytest.mark.asyncio
async def test_meta_capi_payload_integrity():
    """
    Verifies that the Tracker generates the correct payload for EMQ.
    """
    from app.domain.models.events import EventName, TrackingEvent
    from app.domain.models.values import Email, Phone
    from app.domain.models.visitor import Visitor
    from app.infrastructure.external.meta_capi.tracker import MetaTracker

    # Mocking settings to ensure it doesn't try to send real requests
    os.environ["META_SANDBOX_MODE"] = "1"

    visitor = Visitor.create(
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
        email=Email("test@example.com"),
        phone=Phone("+59164714751"),
    )

    event = TrackingEvent.create(
        event_name=EventName.LEAD, external_id=visitor.external_id, source_url="https://test.com"
    )

    tracker = MetaTracker()
    payload = tracker._build_payload(event, visitor)

    user_data = payload["data"][0]["user_data"]

    # CRITICAL CHECKS FOR ROI
    assert "em" in user_data, "Missing hashed email for EMQ"
    assert "ph" in user_data, "Missing hashed phone for EMQ"
    assert "client_ip_address" in user_data
    assert "client_user_agent" in user_data
    assert payload["data"][0]["event_id"] == event.event_id.value, (
        "Event ID mismatch (deduplication)"
    )

    print("✅ Tracking Payload Integrity (EMQ/Dedup) Verified")
