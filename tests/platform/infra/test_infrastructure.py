"""
Infrastructure Integration Tests.

Verifies connectivity and configuration of external services (DB, Redis, etc.).
"""

import logging
import os
import sys
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import psycopg2  # type: ignore
import pytest  # type: ignore
from upstash_redis import Redis  # type: ignore

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

logger = logging.getLogger(__name__)


def test_environment_variables():
    """Verifica que las variables críticas existan"""
    required_vars = [
        "DATABASE_URL",
        "META_PIXEL_ID",
        "META_ACCESS_TOKEN",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN",
    ]

    placeholders = ["SET_IN_PRODUCTION", "stub", "YOUR_TOKEN", "REEMPLAZAR"]
    is_prod = os.getenv("VERCEL") or os.getenv("RENDER")
    is_ci = os.getenv("GITHUB_ACTIONS") or os.getenv("CI")

    # Senior Guard: Audit Mode (Git Sync) is stricter than daily testing
    is_strict_audit = os.getenv("AUDIT_MODE") == "1"

    missing_vars = []
    placeholder_vars = []

    for var_name in required_vars:
        val = getattr(settings, var_name, None)
        if not val:
            missing_vars.append(var_name)
        elif any(p in str(val) for p in placeholders):
            placeholder_vars.append(var_name)

    if missing_vars or placeholder_vars:
        if is_prod:
            pytest.fail(
                f"🚨 PRODUCTION ERROR: Environment issues detected. "
                f"Missing: {missing_vars}, Placeholders: {placeholder_vars}"
            )
        elif is_ci and not is_strict_audit:
            pytest.skip(
                f"💡 CI Mode: Missing secrets {missing_vars}. Skipping integration audit."
            )
        else:
            pytest.skip(
                f"⚠️ Skipping infrastructure integration: "
                f"Detected missing/placeholder variables in {missing_vars + placeholder_vars}. "
                "Configure them for real tests."
            )

    assert True


def test_database_connection():
    """Prueba de conexión a Supabase (Postgres)"""
    db_url = str(settings.DATABASE_URL or "").lower()
    is_prod = os.getenv("VERCEL") or os.getenv("RENDER")

    # Detect placeholders in DSN
    placeholder_patterns = [
        "set_in_production",
        "stub",
        "placeholder",
        "sqlite",
        "required",
    ]
    if not db_url or any(p in db_url for p in placeholder_patterns):
        if is_prod:
            pytest.fail("🚨 PRODUCTION ERROR: DATABASE_URL contains a placeholder.")
        else:
            logger.info(
                "⚠️ Stub/Placeholder DSN detected. Verifying SQLite fallback path."
            )
            from app.database import get_db_connection

            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT 1")
                    assert cur.fetchone() is not None
                pytest.skip(
                    "✅ SQLite connection verified. Skipping real Postgres check (Local)."
                )
            except Exception as e:
                pytest.fail(f"🔥 Fallo conexión SQLite Fallback: {e!s}")

    # Real Postgres Check (only if URL looks valid)
    try:
        parsed = urlparse(settings.DATABASE_URL)
        query = [
            (k, v)
            for k, v in parse_qsl(str(parsed.query))
            if k.lower() not in {"pgbouncer", "connection_limit"}
        ]
        sanitized = urlunparse(parsed._replace(query=urlencode(query)))
        conn = psycopg2.connect(str(sanitized))
        cur = conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone() is not None
        conn.close()
    except (psycopg2.Error, Exception) as e:
        if is_prod:
            pytest.fail(f"🔥 CRITICAL: Production DB Connection failed: {e!s}")
        else:
            pytest.skip(f"💡 Postgres connection skipped (Local): {e!s}")


def test_redis_connection():
    """Prueba de conexión a Upstash Redis"""
    redis_url = str(settings.UPSTASH_REDIS_REST_URL or "")
    is_prod = os.getenv("VERCEL") or os.getenv("RENDER")

    if (
        not redis_url
        or "stub" in redis_url.lower()
        or "set_in_production" in redis_url.lower()
    ):
        if is_prod:
            pytest.fail("🚨 PRODUCTION ERROR: Redis URL is a placeholder.")
        else:
            pytest.skip("⚠️ Redis not configured or stub. Skipping integration check.")

    try:
        redis = Redis(
            url=str(settings.UPSTASH_REDIS_REST_URL),
            token=str(settings.UPSTASH_REDIS_REST_TOKEN),
        )
        ping_result = redis.ping()
        assert ping_result is True or ping_result == "PONG"
    except Exception as e:
        if is_prod:
            pytest.fail(f"🔥 CRITICAL: Production Redis Connection failed: {e!s}")
        else:
            pytest.skip(f"💡 Redis connection skipped (Local): {e!s}")
