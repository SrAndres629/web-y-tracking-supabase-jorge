import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.core.decorators import retry


class TestRetryDecorator:
    """Tests for the retry decorator in app.core.decorators."""

    # --- Sync Tests ---

    def test_sync_success_first_try(self):
        """Test that a sync function succeeds on the first try."""
        mock_func = MagicMock(return_value="success")
        mock_func.__name__ = "mock_func"
        decorated = retry()(mock_func)

        result = decorated()

        assert result == "success"
        mock_func.assert_called_once()

    @patch("time.sleep")
    def test_sync_retry_then_success(self, mock_sleep):
        """Test that a sync function retries and then succeeds."""
        # Fail twice, then succeed
        mock_func = MagicMock(side_effect=[ValueError("fail1"), ValueError("fail2"), "success"])
        mock_func.__name__ = "mock_func"
        decorated = retry(max_attempts=3, base_delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3
        # Should sleep twice
        assert mock_sleep.call_count == 2

    @patch("time.sleep")
    def test_sync_max_retries_exceeded(self, mock_sleep):
        """Test that a sync function raises exception after max retries."""
        mock_func = MagicMock(side_effect=ValueError("persistent fail"))
        mock_func.__name__ = "mock_func"
        decorated = retry(max_attempts=3, base_delay=0.1)(mock_func)

        with pytest.raises(ValueError, match="persistent fail"):
            decorated()

        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2  # Sleeps after 1st and 2nd attempt, not after 3rd failure

    @patch("time.sleep")
    def test_sync_specific_exception(self, mock_sleep):
        """Test that retry only catches specified exceptions."""
        # KeyError is not in (ValueError,)
        mock_func = MagicMock(side_effect=KeyError("unexpected"))
        mock_func.__name__ = "mock_func"
        decorated = retry(max_attempts=3, exceptions=(ValueError,))(mock_func)

        with pytest.raises(KeyError, match="unexpected"):
            decorated()

        assert mock_func.call_count == 1
        mock_sleep.assert_not_called()

    # --- Async Tests ---

    def test_async_success_first_try(self):
        """Test that an async function succeeds on the first try."""
        mock_func = MagicMock(return_value="success")
        mock_func.__name__ = "mock_func"

        @retry()
        async def async_func():
            return mock_func()

        result = asyncio.run(async_func())

        assert result == "success"
        mock_func.assert_called_once()

    def test_async_retry_then_success(self):
        """Test that an async function retries and then succeeds."""
        mock_func = MagicMock(side_effect=[ValueError("fail1"), ValueError("fail2"), "success"])
        mock_func.__name__ = "mock_func"

        @retry(max_attempts=3, base_delay=0.01) # Small delay for test speed
        async def async_func():
            return mock_func()

        async def fake_sleep(delay):
            return None

        with patch("asyncio.sleep", side_effect=fake_sleep) as mock_sleep:
            result = asyncio.run(async_func())

        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2

    def test_async_max_retries_exceeded(self):
        """Test that an async function raises exception after max retries."""
        mock_func = MagicMock(side_effect=ValueError("persistent fail"))
        mock_func.__name__ = "mock_func"

        @retry(max_attempts=3, base_delay=0.01)
        async def async_func():
            return mock_func()

        async def fake_sleep(delay):
            return None

        with patch("asyncio.sleep", side_effect=fake_sleep) as mock_sleep:
            with pytest.raises(ValueError, match="persistent fail"):
                asyncio.run(async_func())

        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2
