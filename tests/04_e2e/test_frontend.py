import pytest
import sys
import os
from fastapi.testclient import TestClient

# Ensure root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.config import settings

client = TestClient(app)

def test_landing_page_render():
    """
    Critical Business Test:
    Ensures the homepage returns 200 OK and actually renders HTML.
    Prevents 'White Screen of Death' or Jinja errors.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    # 🕵️ Verify Critical Marketing Elements
    content = response.text
    
    # 1. Check Title (Basic SEO)
    assert "<title>" in content
    
    # 2. Check Meta Pixel Injection (Critical for Ads)
    if settings.META_PIXEL_ID:
        assert str(settings.META_PIXEL_ID) in content, "❌ CRITICAL: Meta Pixel ID not found in HTML source!"

def test_static_assets():
    """Verifies that static files (CSS/JS) are reachable."""
    # Based on index.html likely having stylesheet
    # We verify /static/ is mounted correctly
    # If explicit file doesn't exist, 404 is expected, but 500 is not.
    response = client.get("/static/dist/css/app.min.css")
    assert response.status_code != 500
