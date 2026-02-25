from unittest.mock import patch
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
from main import app

client = TestClient(app)

def test_onboarding_legal_links():
    """
    Verify that the onboarding page contains correct links to legal documents.
    """
    # Mock the database fetch to avoid "no such table" errors
    with patch("app.services.ContentManager._fetch_from_db", return_value=None):
        response = client.get("/onboarding")

    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the terms link
    terms_link = soup.find("a", string=lambda text: "Términos de" in text if text else False)
    assert terms_link is not None, "Terms link not found"
    assert terms_link["href"] == "/terminos", f"Expected /terminos, got {terms_link['href']}"
    assert terms_link.get("target") == "_blank", "Terms link should open in new tab"
    assert "noopener" in terms_link.get("rel", []), "Terms link missing noopener"
    assert "noreferrer" in terms_link.get("rel", []), "Terms link missing noreferrer"

    # Find the privacy link
    privacy_link = soup.find("a", string=lambda text: "Política de Privacidad" in text if text else False)
    assert privacy_link is not None, "Privacy link not found"
    assert privacy_link["href"] == "/privacidad", f"Expected /privacidad, got {privacy_link['href']}"
    assert privacy_link.get("target") == "_blank", "Privacy link should open in new tab"
    assert "noopener" in privacy_link.get("rel", []), "Privacy link missing noopener"
    assert "noreferrer" in privacy_link.get("rel", []), "Privacy link missing noreferrer"
