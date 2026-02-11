import pytest
import sys
import os
from fastapi.testclient import TestClient

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_app_boot_integrity():
    """
    CRITICAL: Verifies that the FastAPI 'app' object can be imported 
    and initialized without any ImportError or circular dependencies.
    This would have caught the recent 'Request' and 'get_all_visitors' issues.
    """
    try:
        from main import app
        # Create a test client to force initialization of routers/lifespan
        with TestClient(app) as client:
            response = client.get("/health")
            # If health router is missing, it might 404, but the BOOT is what matters
            assert response.status_code in [200, 404] 
        # print("\n✅ System Boot Integrity: VERIFIED")
        pass
    except ImportError as e:
        pytest.fail(f"🔥 BOOT FAILURE: Missing dependency or circular import: {e}")
    except Exception as e:
        pytest.fail(f"🔥 BOOT FAILURE: Unexpected error during startup: {e}")

def test_module_import_consistency():
    """Checks that all core modules are importable"""
    modules = [
        "app.config",
        "app.database",
        "app.tracking",
        "app.interfaces.api.routes.pages",
        "app.services"
    ]
    for mod in modules:
        try:
            __import__(mod)
        except ImportError as e:
            pytest.fail(f"🔥 MODULE FAILURE: Cannot import {mod}. Error: {e}")
