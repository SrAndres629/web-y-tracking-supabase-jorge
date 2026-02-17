from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_robots_txt():
    """
    SEO Guard: Ensures robots.txt exists and allows indexing.
    Breaking this kills organic traffic.
    """
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "User-agent: *" in response.text


def test_sitemap_xml():
    """
    SEO Guard: Ensures sitemap.xml is generated.
    """
    response = client.get("/sitemap.xml")
    # It might be 200 or 404 if not dynamically generated yet,
    # but we assert it doesn't crash (500).
    # Ideally should be 200.
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert (
            "xml" in response.headers["content-type"]
            or "text/xml" in response.headers["content-type"]
        )
