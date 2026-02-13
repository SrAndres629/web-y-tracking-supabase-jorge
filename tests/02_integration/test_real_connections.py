import pytest
import os
import asyncio
from app.config import settings
from app.database import get_db_connection
from redis import asyncio as aioredis

# 🛡️ SILICON VALLEY STANDARD: REAL INFRASTRUCTURE VERIFICATION
# These tests verify actual connectivity to production infrastructure.
# They ALWAYS run — zero-skip policy enforced.

@pytest.mark.asyncio
async def test_real_redis_connection():
    """
    Verifies actual connection to Upstash Redis using credentials from .env
    """
    redis_url = settings.UPSTASH_REDIS_REST_URL
    redis_token = settings.UPSTASH_REDIS_REST_TOKEN
    
    assert redis_url and "upstash.io" in redis_url, "❌ Redis URL invalid or missing in .env"
    assert redis_token, "❌ Redis Token missing in .env"

    redis_conn_url = os.getenv("REDIS_URL")
    assert redis_conn_url, "❌ REDIS_URL (Connection String) missing in .env"

    client = aioredis.from_url(redis_conn_url, encoding="utf-8", decode_responses=True)
    try:
        pong = await client.ping()
        assert pong is True, "❌ Redis PING failed"
    except Exception as e:
        pytest.fail(f"❌ Failed to connect to REAL Redis: {str(e)}")
    finally:
        await client.aclose()

def test_real_database_connection():
    """
    Verifies actual connection to Supabase Postgres using credentials from .env
    """
    assert "supabase.com" in settings.DATABASE_URL, "❌ DATABASE_URL does not look like a Supabase URL"
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                assert result[0] == 1, "❌ Database SELECT 1 returned unexpected result"
    except Exception as e:
        pytest.fail(f"❌ Failed to connect to REAL Database: {str(e)}")

def test_meta_configuration_loaded():
    """
    Verifies that Meta Pixels and Tokens are loaded (not placeholders)
    """
    pixel_id = settings.META_PIXEL_ID
    token = settings.META_ACCESS_TOKEN
    
    assert pixel_id != "SET_IN_PRODUCTION", "❌ META_PIXEL_ID is still a placeholder!"
    assert token != "SET_IN_PRODUCTION", "❌ META_ACCESS_TOKEN is still a placeholder!"
    
    assert pixel_id.isdigit(), f"❌ META_PIXEL_ID should be numeric, got: {pixel_id}"
    assert len(token) > 20, "❌ META_ACCESS_TOKEN looks too short to be valid"

def test_qstash_configuration_loaded():
    """
    Verifies QStash credentials
    """
    assert settings.QSTASH_TOKEN, "❌ QSTASH_TOKEN is missing"
    assert settings.QSTASH_CURRENT_SIGNING_KEY, "❌ QSTASH_CURRENT_SIGNING_KEY is missing"
    assert settings.QSTASH_NEXT_SIGNING_KEY, "❌ QSTASH_NEXT_SIGNING_KEY is missing"
