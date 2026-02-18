from unittest.mock import AsyncMock, patch

import pytest

from app.services import ContentManager, normalize_pii

# 🛡️ THE SERVICES AUDITOR
# =================================================================
# Verifies caching logic, QStash publishing, and content management
# =================================================================


def test_pii_normalization():
    """
    Verifies hygiene PII cleaner
    """
    # Email
    assert normalize_pii("  TEST@Example.com ") == "test@example.com"

    # Phone (Bolivia)
    assert normalize_pii("77712345", mode="phone") == "59177712345"
    assert normalize_pii("+591 777-12345", mode="phone") == "59177712345"

    # Empty
    assert normalize_pii(None) == ""


@pytest.mark.anyio
async def test_content_manager_ram_cache():
    """
    Verifies that L1 RAM cache works instanty
    """
    ContentManager._ram_cache["test_key"] = {"data": "cached"}
    ContentManager._cache_times["test_key"] = 9999999999  # Future

    result = await ContentManager.get_content("test_key")
    assert result == {"data": "cached"}


@pytest.mark.anyio
async def test_content_manager_fallback():
    """
    Verifies that if cache misses, it returns a fallback
    """
    # Clear cache
    ContentManager._ram_cache.clear()

    # Mock background refresh to do nothing (so we isolate fallback logic)
    with patch.object(ContentManager, "_refresh_in_background", new_callable=AsyncMock):
        result = await ContentManager.get_content("services_config")

        # Should return the default list
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["id"] == "microblading"
