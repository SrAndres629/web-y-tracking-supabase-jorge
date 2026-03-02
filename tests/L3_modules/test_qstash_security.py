import hashlib
import base64
import time
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from jose import jwt

from main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_settings():
    """Mock the settings to include QStash keys."""
    # Patch the singleton instance of settings returned by get_settings or the module level settings object
    # Depending on how it's imported.
    # The code uses 'from app.infrastructure.config.settings import settings'
    # So we should patch that object.
    with patch("app.infrastructure.config.settings.settings.external.qstash_current_signing_key", "secret_key_1"),          patch("app.infrastructure.config.settings.settings.external.qstash_next_signing_key", "secret_key_2"):
        yield

def generate_valid_token(payload_bytes, url="http://testserver/hooks/process-event", key="secret_key_1"):
    """Generates a valid QStash JWT for testing."""
    body_hash = hashlib.sha256(payload_bytes).digest()
    body_hash_b64url = base64.urlsafe_b64encode(body_hash).rstrip(b"=").decode("utf-8")

    claims = {
        "iss": "Upstash",
        "sub": url,
        "exp": int(time.time()) + 300,
        "nbf": int(time.time()) - 300,
        "body": body_hash_b64url
    }

    return jwt.encode(claims, key, algorithm="HS256")

def test_qstash_webhook_missing_signature(client):
    """Test request without signature fails."""
    response = client.post("/hooks/process-event", json={"test": "data"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing signature"

def test_qstash_webhook_invalid_signature(client, mock_settings):
    """Test request with invalid signature fails."""
    payload = {"event_name": "Test", "event_id": "123", "event_source_url": "url", "client_ip": "ip", "user_agent": "ua"}
    payload_bytes = json.dumps(payload).encode("utf-8")

    # Generate token with wrong key
    token = generate_valid_token(payload_bytes, key="wrong_key")

    response = client.post(
        "/hooks/process-event",
        content=payload_bytes,
        headers={"Upstash-Signature": token, "Content-Type": "application/json"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"

def test_qstash_webhook_valid_signature(client, mock_settings):
    """Test request with valid signature succeeds."""
    payload = {
        "event_name": "TestEvent",
        "event_id": "test_id",
        "event_source_url": "http://example.com",
        "client_ip": "127.0.0.1",
        "user_agent": "TestAgent",
        "external_id": "test_ext_id",
        "fbc": "fb.1.1234567890.test_fbc",
        "fbp": "test_fbp",
        "phone": "5551234567",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "city": "Test City",
        "state": "Test State",
        "zip_code": "12345",
        "country": "Test Country",
        "custom_data": {},
        "utm_data": {}
    }

    payload_bytes = json.dumps(payload).encode("utf-8")
    token = generate_valid_token(payload_bytes, key="secret_key_1")

    # Mock bg task
    with patch("app.interfaces.api.routes.tracking.bg_send_meta_event", new_callable=AsyncMock) as mock_bg:
        response = client.post(
            "/hooks/process-event",
            content=payload_bytes,
            headers={"Upstash-Signature": token, "Content-Type": "application/json"}
        )

        assert response.status_code == 200
        assert response.json() == {"status": "processed", "source": "qstash"}

        # Also test with next key
        token_2 = generate_valid_token(payload_bytes, key="secret_key_2")
        response_2 = client.post(
            "/hooks/process-event",
            content=payload_bytes,
            headers={"Upstash-Signature": token_2, "Content-Type": "application/json"}
        )
        assert response_2.status_code == 200
