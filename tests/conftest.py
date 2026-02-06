import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Add app to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_settings():
    """Mocks app configuration settings"""
    with patch("app.config.settings") as mock:
        mock.DATABASE_URL = "postgres://user:pass@localhost:5432/db"
        mock.META_PIXEL_ID = "1234567890"
        mock.META_ACCESS_TOKEN = "fake_token"
        yield mock

@pytest.fixture
def mock_db_cursor():
    """Mocks the database cursor context manager"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock the context manager behavior
    with patch("app.database.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_cursor

@pytest.fixture
def mock_redis():
    """Mocks Redis client"""
    with patch("app.main.redis_client") as mock:
        yield mock
