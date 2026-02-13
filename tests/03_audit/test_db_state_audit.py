import pytest
import sqlite3
import os
import importlib
from unittest.mock import patch, MagicMock

# 🛡️ THE DB STATE AUDITOR
# =================================================================
# Verifies that the database schema matches the Source of Truth types.
# =================================================================

@pytest.fixture(scope="function")
def sqlite_db_context():
    """
    Forces app.database to use SQLite by patching settings and reloading the module.
    Restores original state after test.
    """
    # 1. Patch settings to remove DATABASE_URL
    with patch("app.config.settings.DATABASE_URL", None):
        # 2. Reload app.database to re-evaluate BACKEND global
        import app.database
        importlib.reload(app.database)
        
        yield app.database
        
    # 3. Cleanup: Reload again to restore original state (if needed by other tests)
    # in practice, subsequent tests usually start fresh or don't rely on this, 
    # but good hygiene suggests reloading if we modified global state.
    importlib.reload(app.database)

def test_schema_integrity(sqlite_db_context):
    """
    Ensures that critical tables exist and have the correct columns.
    Uses the reloaded sqlite_db_context.
    """
    db_module = sqlite_db_context
    print(f"DEBUG: BACKEND is {db_module.BACKEND}")
    assert db_module.BACKEND == "sqlite"
    
    # Initialize tables (this creates the local sqlite file)
    print("DEBUG: Calling init_tables")
    db_module.init_tables()
    print("DEBUG: init_tables finished")
    
    required_tables = {
        "visitors": ["external_id", "fbclid", "source"],
        "crm_leads": ["whatsapp_phone", "email", "fb_click_id", "lead_score"]
    }
    
    with db_module.get_cursor() as cur:
        for table, columns in required_tables.items():
            # Check table existence
            try:
                cur.execute(f"SELECT * FROM {table} LIMIT 1")
            except Exception:
                pytest.fail(f"🚨 MISSING TABLE: {table}")
            
            # Check column existence (naive check by selecting them)
            params = ", ".join(columns)
            try:
                cur.execute(f"SELECT {params} FROM {table} LIMIT 1")
            except Exception as e:
                pytest.fail(f"🚨 MISSING COLUMN in {table}: {e}")

def test_config_consistency(sqlite_db_context):
    """
    Ensures DB config matches the backend (SQLite vs Postgres logic)
    """
    db_module = sqlite_db_context
    config = db_module._get_db_config()
    
    # Since we forced SQLite
    assert "id_type_uuid" in config
    assert config["id_type_uuid"] == "TEXT PRIMARY KEY"
