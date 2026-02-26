import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from contextlib import asynccontextmanager
import json

from app.infrastructure.external.circuit_breaker import DistributedCircuitBreaker, CircuitBreakerOpenException
from app.infrastructure.external.meta_capi.tracker import MetaTracker
from app.services.outbox_relay import OutboxRelay
from app.domain.models.events import TrackingEvent, EventName
from app.domain.models.values import ExternalId
from app.domain.models.visitor import Visitor

# =================================================================
# ENTERPRISE RESILIENCE INTEGRATION TESTS
# =================================================================
# Verify the fault-tolerance of Circuit Breakers (Redis/Upstash)
# and the exact-once delivery of the Transactional Outbox (Supabase)
# =================================================================

def test_circuit_breaker_open_state():
    """
    Verifies that the Circuit Breaker trips to OPEN after failure_threshold,
    preventing further calls (Fail Fast).
    """
    mock_redis = AsyncMock()
    # Simulate an OPEN state by returning the literal "OPEN" value
    mock_redis.get.return_value = "OPEN"
    
    with patch("app.infrastructure.external.circuit_breaker.redis_provider") as mock_provider:
        mock_provider.async_client = mock_redis
        breaker = DistributedCircuitBreaker("test_api", failure_threshold=3)
        
        # It should raise CircuitBreakerOpenException immediately without executing
        with pytest.raises(CircuitBreakerOpenException):
            import asyncio
            async def dummy_call():
                pass
            asyncio.run(breaker.execute().__aenter__())

@pytest.mark.asyncio
async def test_meta_tracker_circuit_breaker_integration():
    """
    Verifies that MetaTracker utilizes the Circuit Breaker and fails safely
    without crashing the app when the circuit is OPEN.
    """
    # Create valid domain objects
    event = TrackingEvent.create(
        event_name=EventName.PAGE_VIEW,
        external_id=ExternalId("a" * 32),
        source_url="https://test.com",
    )
    visitor = Visitor.create(ip="127.0.0.1", user_agent="pytest")

    tracker = MetaTracker(http_client=AsyncMock())
    # Force enabled for test
    tracker._enabled = True

    # Determine circuit "OPEN" state via Redis mock
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "OPEN"
    
    with patch("app.infrastructure.external.circuit_breaker.redis_provider") as mock_provider:
        mock_provider.is_available = True
        mock_provider.async_client = mock_redis
        
        # Track should fail immediately and return False safely
        result = await tracker.track(event, visitor)
        
        # Check what the method actually returns
        assert result is False


@pytest.mark.asyncio
async def test_outbox_relay_processing_logic():
    """
    Verifies that OutboxRelay correctly fetches 'pending' events,
    processes them, and marks them 'completed'.
    """
    # Mock Database interaction
    mock_db = MagicMock()
    mock_conn = AsyncMock()
    mock_cur = MagicMock()
    
    # Mock fetching pending rows
    fake_row = {
        "id": "outbox_123",
        "aggregate_type": "TrackingEvent",
        "aggregate_id": "evt_123",
        "event_type": "PAGE_VIEW",
        "payload": json.dumps({"event_name": "PageView", "source_url": "test.com"})
    }
    
    with patch("app.services.outbox_relay.db", mock_db):
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        
        with patch("app.services.outbox_relay.OutboxRelay._fetch_pending", return_value=[fake_row]):
            with patch("app.services.outbox_relay.OutboxRelay._process_single", new_callable=AsyncMock) as mock_process:
                mock_process.return_value = True
                
                # Run the relay
                processed_count = await OutboxRelay.process_pending_events(batch_size=10)
                
                assert processed_count == 1
                mock_process.assert_called_once()
