from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock
from app.limiter import limiter
from app.config import settings

# Disable rate limiting for tests
limiter.enabled = False

# FORCE STRICT SECURITY: Ensure Secret Key is "present" so logic doesn't bypass
settings.TURNSTILE_SECRET_KEY = "dummy_secret_for_test"

client = TestClient(app)

def test_zero_tolerance_turnstile_missing():
    """
    🛡️ ARCHITECTURAL AUDIT: Zero Tolerance Policy (Missing Token)
    Attempts to send a critical event (Lead) without a Turnstile token.
    MUST fail with 403 or "Signal filtered".
    """
    payload = {
        "event_name": "Lead",
        "event_time": 1234567890,
        "event_id": "evt_123_hack",
        "user_data": {"email": "bot@hack.com"},
        "event_source_url": "https://hack.com",
        "custom_data": {} # ❌ NO TOKEN
    }
    
    # We mock validate_turnstile to return False just in case (though missing token should fail before)
    # Actually, logic in tracking_routes.py _validate_human checks custom_data.get("turnstile_token")
    
    response = client.post("/track/event", json=payload)
    
    # Trace deleted for architecture compliance
    # assert response.status_code == 200 # Logic check later

    # It might return 200 with "Signal filtered" message per current implementation
    # or 403 Forbidden. We accept either as long as it's NOT "queued".
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] != "queued", "❌ SECURITY HOLE: Backend accepted event without Turnstile token!"
    assert "filtered" in json_resp.get("message", "").lower(), "❌ Expected 'filtered' message for missing token"


@patch("app.routes.tracking_routes.validate_turnstile", new_callable=AsyncMock)
def test_zero_tolerance_turnstile_invalid(mock_validate):
    """
    🛡️ ARCHITECTURAL AUDIT: Zero Tolerance Policy (Invalid Token)
    Attempts to send a critical event with a FAKE token.
    MUST fail.
    """
    # Mock Turnstile failure
    mock_validate.return_value = False
    
    payload = {
        "event_name": "Lead",
        "event_time": 1234567890,
        "event_id": "evt_123_hack_2",
        "user_data": {"email": "bot@hack.com"},
        "event_source_url": "https://hack.com",
        "custom_data": {"turnstile_token": "INVALID_TOKEN_XYZ"}
    }
    
    response = client.post("/track/event", json=payload)
    
    json_resp = response.json()
    assert json_resp["status"] != "queued", "❌ SECURITY HOLE: Backend accepted event with INVALID token!"
    assert "filtered" in json_resp.get("message", "").lower(), "❌ Expected 'filtered' message for invalid token"
