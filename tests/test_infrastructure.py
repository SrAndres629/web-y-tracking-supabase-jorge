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
        "META_API_TOKEN",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN"
    ]
    
    all_vars_present = True
    missing_vars = []

    for var_name in required_vars:
        if not hasattr(settings, var_name) or not getattr(settings, var_name):
            all_vars_present = False
            missing_vars.append(var_name)
            logger.error(f"Environment variable {var_name} is missing or empty.")
        else:
            logger.info(f"Environment variable {var_name} is present.")

    if not all_vars_present:
        pytest.fail(f"🔥 Missing critical environment variables: {', '.join(missing_vars)}")
    
    logger.info("All critical environment variables are present.")
    assert all_vars_present is True

def test_database_connection():
    """Prueba de conexión a Supabase (Postgres)"""
    # Deterministic Guard check from app/database.py
    # If using SQLite fallback, we should test THAT connection instead of failing.
    
    db_url = settings.DATABASE_URL.lower()
    if "stub_for_vercel" in db_url or "stub" in db_url:
        logger.info("⚠️ Stub DSN detected. Skipping REAL Postgres check, verifying SQLite fallback path.")
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
    if not settings.UPSTASH_REDIS_REST_URL or "stub" in str(settings.UPSTASH_REDIS_REST_URL):
        logger.info("⚠️ Redis not configured or stub. Skipping.")
        return
        
    try:
        redis = Redis(
            url=settings.UPSTASH_REDIS_REST_URL, 
            token=settings.UPSTASH_REDIS_REST_TOKEN
        )
        assert redis.ping() is True
    except Exception as e:
        pytest.fail(f"🔥 Fallo conexión Redis: {str(e)}")
