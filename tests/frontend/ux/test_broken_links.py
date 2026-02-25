from fastapi.testclient import TestClient
from main import app
import re
import pytest

client = TestClient(app)

def test_onboarding_legal_links():
    """Verify onboarding page has correct legal links."""
    response = client.get("/onboarding")
    assert response.status_code == 200
    html = response.text

    # Check Terms link
    assert re.search(r'href="/terminos"', html), "❌ Terms link should point to /terminos in Onboarding"

    # Check Privacy link
    assert re.search(r'href="/privacidad"', html), "❌ Privacy link should point to /privacidad in Onboarding"

def test_footer_legal_links():
    """Verify footer (on home page) has correct legal links."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Check Privacy link
    assert re.search(r'href="/privacidad"', html), "❌ Footer Privacy link should point to /privacidad"

    # Check Terms link
    assert re.search(r'href="/terminos"', html), "❌ Footer Terms link should point to /terminos"

    # Check Sitemap link
    assert re.search(r'href="/sitemap\.xml"', html), "❌ Footer Sitemap link should point to /sitemap.xml"
