import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.meta_capi import EliteMetaCAPIService, EnhancedUserData

# 🛡️ THE META CAPI AUDITOR
# =================================================================
# Verifies the elite service logic for Meta Conversions API
# =================================================================


@pytest.fixture
def capi_service():
    """Returns a fresh instance of EliteMetaCAPIService for each test"""
    return EliteMetaCAPIService()


def test_enhanced_user_data_hashing():
    """
    Verifies that EnhancedUserData automatically normalizes and prepares data
    """
    user_data = EnhancedUserData(
        email="  Jorge@Example.COM  ", phone="+591-777-12345", city="Santa Cruz ", country="BO"
    )

    # We mock SDK classes to inspect what is sent
    # But here we can inspect the object itself or its to_sdk_user_data method result
    # For unit testing without SDK, we check the normalization logic in _set_* methods
    # But since those modify SDK objects, we need to mock UserData

    with patch("app.meta_capi.SDK_AVAILABLE", True):
        with patch("app.meta_capi.UserData") as MockUserData:
            mock_ud = MockUserData.return_value
            user_data.to_sdk_user_data()

            # Verify Hashing (SHA256: 64 hex chars)
            sha256_pattern = re.compile(r"^[a-f0-9]{64}$")

            # Verify Email Hashing
            assert sha256_pattern.match(mock_ud.email)

            # Verify Phone Hashing
            assert sha256_pattern.match(mock_ud.phone)

            # Verify City Hashing
            assert sha256_pattern.match(mock_ud.city)

            # Verify Country Hashing
            assert sha256_pattern.match(mock_ud.country_code)


@pytest.mark.asyncio
async def test_deduplication_logic(capi_service):
    """
    Verifies that duplicate events are blocked
    """
    event_id = "evt_123"
    event_name = "Purchase"

    # Mock deduplicate to return False (Duplicate found)
    capi_service._deduplicate = MagicMock(return_value=False)

    result = await capi_service.send_event(
        event_name=event_name,
        event_id=event_id,
        event_source_url="http://test.com",
        user_data=EnhancedUserData(),
    )

    assert result["status"] == "duplicate"
    assert result["event_id"] == event_id


@pytest.mark.asyncio
async def test_sandbox_interception(capi_service):
    """
    Verifies that Sandbox Mode prevents sending
    """
    capi_service.sandbox_mode = True

    result = await capi_service.send_event(
        event_name="Lead",
        event_id="evt_test",
        event_source_url="http://test.com",
        user_data=EnhancedUserData(),
    )

    assert result["status"] == "sandbox"


@pytest.mark.asyncio
async def test_fallback_mechanism(capi_service):
    """
    Verifies that if SDK is missing, it falls back to HTTP
    """
    with patch("app.meta_capi.SDK_AVAILABLE", False):
        with patch("app.meta_capi.send_event_async", new_callable=AsyncMock) as mock_http_send:
            mock_http_send.return_value = True

            user_data = EnhancedUserData(email="test@test.com")

            result = await capi_service.send_event(
                event_name="Lead",
                event_id="evt_fallback",
                event_source_url="http://test.com",
                user_data=user_data,
            )

        assert result["status"] == "success"
        assert result["method"] == "http_fallback"
        mock_http_send.assert_called_once()
