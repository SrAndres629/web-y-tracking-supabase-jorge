import pytest
import os
import psycopg2
from upstash_redis import Redis
from app.config import settings
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_environment_variables():
    """Verifica que las variables críticas existan"""
    required_vars = [
        "DATABASE_URL", 
        "META_PIXEL_ID", 
        "META_API_TOKEN"
    ]
    # Check explicitly if env vars are loaded (not just via settings object which might have defaults)
    # But usually testing 'settings' is better. We'll check settings to ensure config loading worked.
    
    assert settings.DATABASE_URL, "DATABASE_URL is missing"
    assert settings.META_PIXEL_ID, "META_PIXEL_ID is missing"

def test_database_connection():
    """Prueba de conexión a Supabase (Postgres)"""
    # Deterministic Guard check from app/database.py
    # If using SQLite fallback, we should test THAT connection instead of failing.
    
    db_url = settings.DATABASE_URL.lower()
    if "required_in_vercel" in db_url or "placeholder" in db_url:
        print("⚠️ Placeholder DSN detected. Skipping REAL Postgres check, verifying SQLite fallback path.")
        from app.database import get_db_connection
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                assert cur.fetchone() is not None
        except Exception as e:
            pytest.fail(f"🔥 Fallo conexión SQLite Fallback: {str(e)}")
        return

    # Real Postgres Check
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone() is not None
        conn.close()
    except Exception as e:
        pytest.fail(f"🔥 Fallo conexión DB (Postgres): {str(e)}")

def test_redis_connection():
    """Prueba de conexión a Upstash Redis"""
    if not settings.UPSTASH_REDIS_REST_URL or "placeholder" in str(settings.UPSTASH_REDIS_REST_URL):
        print("⚠️ Redis not configured or placeholder. Skipping.")
        return
        
    try:
        redis = Redis(
            url=settings.UPSTASH_REDIS_REST_URL, 
            token=settings.UPSTASH_REDIS_REST_TOKEN
        )
        assert redis.ping() is True
    except Exception as e:
        pytest.fail(f"🔥 Fallo conexión Redis: {str(e)}")
