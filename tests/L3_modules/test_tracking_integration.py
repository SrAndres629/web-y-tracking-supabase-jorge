from unittest.mock import patch

from app.domain.validation.event_validator import event_validator
from app.tracking import _build_payload, send_event


def test_build_payload_validation():
    """Test that build_payload triggers validator warnings."""
    with patch("app.tracking.logger") as mock_logger:
        # Invalid email
        _ = _build_payload(
            event_name="Test",
            event_source_url="http://test.com",
            client_ip="1.1.1.1",
            user_agent="test-ua",
            event_id="evt_123",
            email="invalid-email",
        )
        # Check logs for warning
        warnings = [
            call.args[0]
            for call in mock_logger.warning.call_args_list
            if "⚠️ [VALIDATION]" in str(call)
        ]
        assert any("Invalid Email Format" in w for w in warnings)


@patch("app.tracking.sync_client.post")
@patch("app.tracking.dedup_service.try_consume_event")
@patch("app.tracking._log_emq")
def test_send_event_success(mock_log, mock_dedup, mock_post):
    """Test successful event sending with validation pass."""
    mock_dedup.return_value = True  # New event
    mock_post.return_value.status_code = 200

    success = send_event(
        event_name="PageView",
        event_source_url="http://test.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_test_success",
        email="test@example.com",
    )

    assert success is True
    mock_dedup.assert_called_once()
    mock_post.assert_called_once()


@patch("app.tracking.dedup_service.try_consume_event")
def test_deduplication_skips_send(mock_dedup):
    """Test that duplicate events are skipped (return True)."""
    mock_dedup.return_value = False  # Duplicate!

    with patch("app.tracking.sync_client.post") as mock_post:
        success = send_event(
            event_name="PageView",
            event_source_url="http://test.com",
            client_ip="127.0.0.1",
            user_agent="TestAgent",
            event_id="evt_test_duplicate",
        )

        assert success is True  # Returns True because it's handled (skipped)
        mock_post.assert_not_called()


def test_validator_schema_rejection():
    """Test that invalid payload structure is caught."""
    # Build a payload manually with missing required field
    payload = {
        "event_name": "Test",
        # Missing event_time, event_id, user_data...
    }
    assert event_validator.validate_payload(payload) is False

    # Valid payload
    valid_payload = {
        "data": [
            {
                "event_name": "Test",
                "event_time": 1234567890,
                "event_id": "evt_123",
                "action_source": "website",
                "user_data": {"client_ip_address": "1.1.1.1"},
                "event_source_url": "http://test.com",
            }
        ],
        "access_token": "token",
    }
    assert event_validator.validate_payload(valid_payload) is True
