import os
import pytest
from app.infrastructure.config.settings import Settings

def test_database_url_alias_contract():
    """
    CONTRACT: DATABASE_URL must be correctly aliased to settings.db.url.
    This prevents the fallback-to-sqlite catastrophe in production.
    """
    test_url = "postgresql://user:pass@host:5432/db"
    os.environ["DATABASE_URL"] = test_url
    
    # Force fresh settings by clearing Pydantic cache if needed or just re-instantiating
    settings = Settings(_env_file=None)
    
    assert settings.db.url == test_url, (
        "🔥 CONTRACT BREACH: DATABASE_URL alias is not correctly mapping to Settings.db.url. "
        "Check app/infrastructure/config/settings.py for correct Field(alias='DATABASE_URL') definition."
    )
    
    assert settings.db.is_configured is True, "🔥 CONTRACT BREACH: Database should be marked as configured when URL is present."

def test_critical_env_visibility():
    """
    CONTRACT: Critical variables MUST be visible to the Pydantic model.
    """
    critical_vars = {
        "META_PIXEL_ID": "123456",
        "META_ACCESS_TOKEN": "token_abc"
    }
    
    for key, val in critical_vars.items():
        os.environ[key] = val
        
    settings = Settings()
    
    assert settings.meta.pixel_id == "123456", f"🔥 FAILED: META_PIXEL_ID not loaded. Check alias."
    assert settings.meta.access_token == "token_abc", f"🔥 FAILED: META_ACCESS_TOKEN not loaded. Check alias."

def test_vercel_fail_fast_contract():
    """
    CONTRACT: In VERCEL environment, if DB is missing, it MUST raise RuntimeError.
    """
    from app.infrastructure.persistence.database import Database
    from unittest.mock import MagicMock
    
    # Mock settings to be unconfigured
    mock_settings = MagicMock()
    mock_settings.db.is_configured = False
    
    os.environ["VERCEL"] = "1"
    
    with pytest.raises(RuntimeError) as excinfo:
        # Instantiation now triggers the fail-fast check
        manager = Database(settings=mock_settings)
    
    assert "CRITICAL: DATABASE_URL is missing" in str(excinfo.value)
    
    # Cleanup
    if "VERCEL" in os.environ:
        del os.environ["VERCEL"]
