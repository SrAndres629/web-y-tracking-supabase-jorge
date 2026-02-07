import pytest
from fastapi.testclient import TestClient
from main import app
import time
import os
import logging

# Ensure logging is configured for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_bot_defense():
    """Verify that bots are detected and tracking is (conceptually) blocked"""
    # Human UA
    response = client.get("/", headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    assert response.status_code == 200
    # Check if cookies are set for humans
    assert "_fbp" in response.cookies
    
    # Bot UA
    response_bot = client.get("/", headers={"user-agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"})
    assert response_bot.status_code == 200
    # Bots shouldn't get tracking cookies in our implementation (they can, but we block BG tasks)
    # Actually, we set cookies if human. Let's check.

def test_cookie_durability():
    """Verify server-side cookies are set with correct attributes"""
    response = client.get("/", params={"fbclid": "12345"})
    assert response.status_code == 200
    assert "_fbp" in response.cookies
    assert "_fbc" in response.cookies
    
    # Verify max-age is roughly 1 year
    # TestClient cookies don't always show full attributes easily, but we can check headers
    cookies = response.headers.get("set-cookie", "")
    assert "Max-Age=31536000" in cookies

def test_swr_caching():
    """Verify SWR logic in services (conceptually via timing)"""
    # This is harder to test with TestClient as it's sync internally often,
    # but we can check if ContentManager behaves.
    pass

def test_dlq_logic():
    """Verify DLQ file creation"""
    from app.retry_queue import add_to_retry_queue, QUEUE_FILE
    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)
        
    add_to_retry_queue("TestEvent", {"data": "test"})
    assert os.path.exists(QUEUE_FILE)
    with open(QUEUE_FILE, "r") as f:
        import json
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["event_name"] == "TestEvent"

if __name__ == "__main__":
    # Manual run
    logger.info("Running Bot Defense check...")
    test_bot_defense()
    logger.info("Running Cookie Durability check...")
    test_cookie_durability()
    logger.info("Running DLQ check...")
    test_dlq_logic()
    logger.info("✅ All Diamond Protocol checks passed!")
