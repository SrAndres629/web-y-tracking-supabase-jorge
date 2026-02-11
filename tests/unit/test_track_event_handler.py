import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.commands.track_event import TrackEventHandler, TrackEventCommand
from app.application.dto.tracking_dto import TrackEventRequest, TrackingContext
from app.domain.models.events import EventName, TrackingEvent
from app.domain.models.values import ExternalId, UTMParams
from app.domain.models.visitor import Visitor, VisitorSource

@pytest.fixture
def mock_deduplicator():
    return AsyncMock()

@pytest.fixture
def mock_visitor_repo():
    return AsyncMock()

@pytest.fixture
def mock_event_repo():
    return AsyncMock()

@pytest.fixture
def mock_tracker_port():
    mock = AsyncMock()
    mock.name = "MockTracker" # Add a name for logging purposes
    return mock

@pytest.fixture
def handler(mock_deduplicator, mock_visitor_repo, mock_event_repo, mock_tracker_port):
    return TrackEventHandler(
        deduplicator=mock_deduplicator,
        visitor_repo=mock_visitor_repo,
        event_repo=mock_event_repo,
        trackers=[mock_tracker_port],
    )

@pytest.fixture
def base_request():
    return TrackEventRequest(
        event_name="PageView",
        external_id="test-external-id",
        source_url="http://example.com",
        fbclid="fb-clid",
        fbp="fbp-id",
        utm_source="source",
        utm_medium="medium",
        utm_campaign="campaign",
    )

@pytest.fixture
def base_context():
    return TrackingContext(
        ip_address="127.0.0.1",
        user_agent="TestAgent",
    )

@pytest.mark.asyncio
async def test_handle_invalid_event_name(handler, base_request, base_context):
    base_request.event_name = "InvalidEvent"
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert not response.success
    assert "Invalid event name" in response.message

@pytest.mark.asyncio
async def test_handle_invalid_external_id(handler, base_request, base_context):
    base_request.external_id = "" # ExternalId cannot be empty
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert not response.success
    assert "ExternalId cannot be empty" in response.message

@pytest.mark.asyncio
async def test_handle_duplicate_event(handler, mock_deduplicator, base_request, base_context):
    mock_deduplicator.is_unique.return_value = False
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert not response.success
    assert response.status == "duplicate"
    mock_deduplicator.is_unique.assert_called_once()

@pytest.mark.asyncio
async def test_handle_new_visitor_and_event_saved(
    handler, mock_deduplicator, mock_visitor_repo, mock_event_repo, mock_tracker_port, base_request, base_context
):
    mock_deduplicator.is_unique.return_value = True
    mock_visitor_repo.get_by_external_id.return_value = None # No existing visitor
    
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert response.success
    assert response.status == "queued"
    
    mock_deduplicator.is_unique.assert_called_once()
    mock_visitor_repo.get_by_external_id.assert_called_once_with(ExternalId(base_request.external_id))
    
    # Verify new visitor was created and saved
    mock_visitor_repo.save.assert_called_once()
    saved_visitor = mock_visitor_repo.save.call_args[0][0]
    assert isinstance(saved_visitor, Visitor)
    assert saved_visitor.ip == base_context.ip_address
    assert saved_visitor.fbclid == base_request.fbclid
    
    # Verify event was created and saved
    mock_event_repo.save.assert_called_once()
    saved_event = mock_event_repo.save.call_args[0][0]
    assert isinstance(saved_event, TrackingEvent)
    assert saved_event.event_name == EventName(base_request.event_name)
    assert saved_event.external_id.value == base_request.external_id
    
    # Verify tracker was called (create_task runs in background, so we check the mock call)
    # We need a slight delay or explicit call to run the background task
    # For unit tests, typically we just assert the call was made, or patch asyncio.create_task
    # Here, we'll ensure the tracker.track mock was called
    # Note: direct assertion on async_mock might need a small await or run_until_complete
    
    # Give asyncio.create_task a chance to schedule the mock tracker call
    await asyncio.sleep(0.01) 
    mock_tracker_port.track.assert_called_once_with(saved_event, saved_visitor)

@pytest.mark.asyncio
async def test_handle_existing_visitor_updated_and_event_saved(
    handler, mock_deduplicator, mock_visitor_repo, mock_event_repo, mock_tracker_port, base_request, base_context
):
    mock_deduplicator.is_unique.return_value = True
    
    existing_visitor = Visitor.create(
        ip="192.168.1.1", user_agent="OldAgent", source=VisitorSource.PAGEVIEW
    )
    existing_visitor._external_id = ExternalId(base_request.external_id) # Manually set external_id for mock
    mock_visitor_repo.get_by_external_id.return_value = existing_visitor
    
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert response.success
    
    mock_visitor_repo.get_by_external_id.assert_called_once_with(ExternalId(base_request.external_id))
    
    # Verify existing visitor was updated
    mock_visitor_repo.update.assert_called_once_with(existing_visitor)
    assert existing_visitor.fbclid == base_request.fbclid # Should be updated
    assert existing_visitor.fbp == base_request.fbp
    assert existing_visitor.visits > 1 # record_visit was called
    
    # Verify event was created and saved
    mock_event_repo.save.assert_called_once()
    
    await asyncio.sleep(0.01) # Allow background task to schedule
    mock_tracker_port.track.assert_called_once()

@pytest.mark.asyncio
async def test_handle_exception_during_processing(handler, mock_deduplicator, base_request, base_context):
    mock_deduplicator.is_unique.side_effect = Exception("Deduplicator error")
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert not response.success
    assert "Deduplicator error" in response.message

@pytest.mark.asyncio
async def test_send_to_trackers_no_trackers(handler, mock_deduplicator, mock_visitor_repo, mock_event_repo, base_request, base_context):
    # Test _send_to_trackers directly with no trackers configured
    handler.trackers = []
    
    # Simulate an event and visitor for _send_to_trackers
    event = TrackingEvent.create(
        event_name=EventName.PAGEVIEW,
        external_id=ExternalId("test"),
        source_url="http://test.com"
    )
    visitor = Visitor.create(ip="1.1.1.1", user_agent="test", source=VisitorSource.DIRECT)

    # Call the protected method directly - generally not ideal for unit testing,
    # but for testing a helper it's sometimes necessary.
    # A better approach might be to ensure `create_task` is called, and then check what it was called with.
    # However, since we're testing the internal logic of _send_to_trackers, direct call is acceptable here.
    
    # Ensure no exception is raised
    await handler._send_to_trackers(event, visitor)
    assert True # If no exception, test passes.

@pytest.mark.asyncio
async def test_send_to_trackers_tracker_failure(
    handler, mock_deduplicator, mock_visitor_repo, mock_event_repo, mock_tracker_port, base_request, base_context
):
    mock_deduplicator.is_unique.return_value = True
    mock_visitor_repo.get_by_external_id.return_value = None
    mock_tracker_port.track.side_effect = Exception("Tracker network error")
    
    cmd = TrackEventCommand(request=base_request, context=base_context)
    
    response = await handler.handle(cmd)
    
    assert response.success # Main handle should still succeed even if tracker fails in background
    assert response.status == "queued"
    
    await asyncio.sleep(0.01) # Allow background task to schedule
    mock_tracker_port.track.assert_called_once()
    # Check if the error was logged (can't directly assert log, but important to know it's handled)
