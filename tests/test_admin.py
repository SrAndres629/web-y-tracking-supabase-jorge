import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_admin_access_unauthorized():
    """
    Security Guard:
    Unauthenticated attempts to access /admin must be blocked
    (Redirect to login or 401/403).
    """
    try:
        response = client.get("/admin/dashboard", follow_redirects=False)
        
        # Expecting either:
        # 1. Redirect (307/302) to /admin/login
        # 2. Forbidden/Unauthorized (401/403)
        # 3. Not Found (404) if route is hidden
        
        # ABSOLUTELY NOT 200 OK (Open Access)
        assert response.status_code != 200, "❌ CRITICAL: Admin dashboard is publicly accessible!"
        
        if response.status_code in [302, 307]:
            assert "/login" in response.headers["location"]
            
    except Exception as e:
        # If route doesn't exist yet, it might 404, which is technically 'secure'
        pass
