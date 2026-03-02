from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_onboarding_legal_links():
    """
    Verifies that the onboarding page contains the correct legal links
    with proper target attributes.
    """
    response = client.get("/onboarding")
    assert response.status_code == 200
    content = response.text

    # Check for Terms link
    assert 'href="/terminos"' in content, "Terms link should point to /terminos"

    # Check for Privacy link
    assert 'href="/privacidad"' in content, "Privacy link should point to /privacidad"

    # Check for target="_blank" to ensure new tab opening
    # We check specifically in the context of these links if possible,
    # but for now ensuring the string exists in the response is a good start
    # given we just added them.
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content
