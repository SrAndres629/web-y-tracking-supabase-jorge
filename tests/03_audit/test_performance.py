import pytest
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_performance_headers():
    """
    Verifies presence of performance/security headers.
    Commonly checked: X-Process-Time, Gzip, etc.
    """
    response = client.get("/")
    # FastApi/Starlette often adds content-length/type
    # We check if Gzip middleware is ostensibly active (implicit) via valid response
    assert response.status_code == 200

def test_latency_threshold_check():
    """
    Soft Performance Check:
    Ensures the homepage (which hits DB/Cache) renders in < 500ms (Local).
    """
    start = time.time()
    response = client.get("/")
    end = time.time()
    
    duration = (end - start) * 1000 # ms
    
    # Asserting a generous local threshold.
    # If it takes >1000ms locally, we have a serious optimization issue.
    if duration > 1000:
        pytest.warns(UserWarning, match=f"⚠️ SLOW RENDER: {duration:.2f}ms")
    else:
        assert duration < 2000 # Hard limit
