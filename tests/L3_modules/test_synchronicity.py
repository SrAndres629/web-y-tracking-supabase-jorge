import pytest
from fastapi.testclient import TestClient
from main import app
import re

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_global_synchronicity_headers(client):
    """Verify that the root HTML forces revalidation (No-Cache)"""
    response = client.get("/")
    assert response.status_code == 200
    
    # Silicon Valley Standard Headers
    assert response.headers.get("Cache-Control") == "no-cache, no-store, must-revalidate"
    assert response.headers.get("Pragma") == "no-cache"
    assert response.headers.get("Expires") == "0"

def test_deterministic_asset_versioning(client):
    """Verify that assets include a numeric ?v= parameter"""
    response = client.get("/")
    html = response.text
    
    # Check app.min.css
    # Pattern: /static/dist/css/app.min.css?v=[any_number]
    assert "/static/dist/css/app.min.css?v=" in html
    
    # Extract version
    match = re.search(r'app\.min\.css\?v=(\d+)', html)
    assert match is not None, "Version parameter missing from app.min.css"
    
    version = match.group(1)
    assert len(version) >= 10, "Version should be a long timestamp"

def test_version_consistency_across_assets(client):
    """Ensure all local static assets use the EXACT same version ID"""
    response = client.get("/")
    html = response.text
    
    versions = re.findall(r'\?v=(\d+)', html)
    
    if versions:
        # All detected versions must be identical
        assert all(v == versions[0] for v in versions), f"Inconsistent versions detected: {set(versions)}"
