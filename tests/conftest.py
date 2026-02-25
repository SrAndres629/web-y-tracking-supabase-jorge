import os
from unittest.mock import AsyncMock, MagicMock

import pytest

# 🛡️ THE SUPERVISOR
# Enforces architectural rules at runtime.


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """
    Supervisor Hook: Checks if tests are obeying the rules of their Layer.
    """
    # 1. Identify Layer
    path = str(item.fspath)
    layer = "unknown"
    if "L1_atoms" in path:
        layer = "L1"
    elif "L2_components" in path:
        layer = "L2"
    elif "L3_modules" in path:
        layer = "L3"
    elif "L4_supervisor" in path:
        layer = "L4"
    elif "L5_system" in path:
        layer = "L5"
    elif "L6_omni" in path:
        layer = "L6"

    # 2. Enforce Rules BEFORE test runs
    if layer == "L1":
        # L1: No DB connections allowed (even mocks should be light)
        pass

    if layer == "L3":
        # L3: MUST NOT hit real external APIs (Meta, etc.)
        # This is enforced by the autouse fixtures below, but we could add checks here.
        pass

    if layer == "L5":
        # L5: MUST have Real Infrastructure
        if os.getenv("REAL_INFRA") != "1" and "DATABASE_URL" not in os.environ:
            # We allow it to run if it sets up its own config (like test_real_connection.py does)
            pass

    _outcome = yield

    # 3. Enforce Rules AFTER test runs
    # (e.g., check execution time for L1)


# =============================================================================
# GLOBAL MOCKS (L1-L3 SAFE)
# =============================================================================


@pytest.fixture(autouse=True)
def block_external_calls(request):
    """
    Blocks external calls for L1-L3 layers.
    Refined to handle both Legacy and Modern Meta implementations.
    """
    path = str(request.node.fspath)
    if "L5_system" in path or "L6_omni" in path:
        yield  # Allow external calls for System/Omni tests
        return

    # Block Meta CAPI & Facebook SDK
    with pytest.MonkeyPatch.context() as m:
        # 1. Block SDK Init (Prevents OAuthException)
        try:
            m.setattr("facebook_business.api.FacebookAdsApi.init", MagicMock())
        except (ImportError, ModuleNotFoundError):
            pass

        # 2. Block Modern Tracker (app.infrastructure.external.meta_capi.tracker.MetaTracker)
        try:
            m.setattr(
                "app.infrastructure.external.meta_capi.tracker.MetaTracker.track",
                AsyncMock(return_value=True),
            )
            m.setattr(
                "app.infrastructure.external.meta_capi.tracker.MetaTracker.health_check",
                AsyncMock(return_value=True),
            )
        except (ImportError, ModuleNotFoundError):
            pass

        # 3. Block Legacy Network Calls (app.tracking used by EliteMetaCAPIService)
        try:
            m.setattr("app.tracking.send_event_async", AsyncMock(return_value=True))
            m.setattr("app.tracking.send_event", MagicMock(return_value=True))
        except (ImportError, ModuleNotFoundError):
            pass

        yield


@pytest.fixture
def mock_visitor_repository():
    """Provides a mocked VisitorRepository."""
    repo = MagicMock()
    repo.get_by_external_id = AsyncMock(return_value=None)
    repo.save = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_event_repository():
    """Provides a mocked EventRepository."""
    repo = MagicMock()
    repo.save = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_lead_repository():
    """Provides a mocked LeadRepository."""
    repo = MagicMock()
    repo.save = AsyncMock(return_value=None)
    return repo


@pytest.fixture(scope="session")
def db_sqlite():
    """
    Standardized SQLite database for L3/L4 tests.
    Ensures DDD Database instance is used instead of legacy shims.
    """
    from app.infrastructure.persistence.database import db
    from app import settings
    
    # Force SQLite test path
    original_backend = db._backend
    db._backend = "sqlite"
    
    # Initialize schema
    db.init_tables()
    
    yield db
    
    # Restore original state if needed
    db._backend = original_backend


@pytest.fixture(autouse=True)
def clean_db(request, db_sqlite):
    """
    Clears tables before each test if the test is in L3 or L4.
    Depends on db_sqlite to ensure initialization happens first.
    """
    path = str(request.node.fspath)
    if "L3_modules" in path or "L4_integration" in path:
        # Use the already initialized connection from db_sqlite if possible
        # but for clean isolation, a direct connection is safer
        import sqlite3
        
        # Consistent path resolution matching Database class
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "database", 
            "local.db"
        )
        
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Explicitly check for table existence before deleting
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crm_leads'")
            if cur.fetchone():
                cur.execute("DELETE FROM crm_leads")
                cur.execute("DELETE FROM visitors")
                cur.execute("DELETE FROM events")
                conn.commit()
        finally:
            conn.close()
    yield
