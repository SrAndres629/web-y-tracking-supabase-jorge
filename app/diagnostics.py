"""
🔍 System Diagnostics Module.

Diagnostics using the DDD infrastructure layer (db singleton, settings).
No legacy imports.
"""
import logging
import os
import sys
from typing import Any, Dict

from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


def check_environment() -> Dict[str, Any]:
    """Audit environment variables and system info."""

    def mask(val):
        return f"{val[:4]}...{val[-4:]}" if val and len(val) > 8 else ("SET" if val else "MISSING")

    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "env_vars": {
            "DATABASE_URL": mask(settings.DATABASE_URL),
            "UPSTASH_REDIS_REST_URL": mask(settings.UPSTASH_REDIS_REST_URL),
            "META_PIXEL_ID": settings.META_PIXEL_ID,
            "VERCEL_ENV": os.getenv("VERCEL_ENV", "local"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "unset"),
        },
        "meta_capi": "READY"
        if settings.META_ACCESS_TOKEN and settings.META_PIXEL_ID
        else "NOT_CONFIGURED",
        "api_status": "OPERATIONAL",
        "db_mode": "PROD" if "localhost" not in (settings.DATABASE_URL or "") else "LOCAL_DEV",
    }


def check_database() -> Dict[str, Any]:
    """Verify database connection using the db singleton."""
    status = {"status": "unknown", "backend": "none", "details": ""}
    try:
        if settings.DATABASE_URL == "STUB_FOR_VERCEL":
            return {"status": "skipped", "details": "INVALID_DATABASE_URL_STUB"}

        if not settings.DATABASE_URL:
            return {"status": "failed", "details": "DATABASE_URL not set"}

        # Use the db singleton for health check
        with db.connection() as conn:
            cur = conn.cursor()
            if db.backend == "sqlite":
                cur.execute("SELECT sqlite_version();")
            else:
                cur.execute("SELECT version();")
            row = cur.fetchone()
            v = row[0] if row else "Unknown"
            status["status"] = "ok"
            status["backend"] = db.backend
            status["details"] = v

    except Exception as e:
        status["status"] = "error"
        status["details"] = str(e)

    return status


def check_redis() -> Dict[str, Any]:
    """Verify Redis/Upstash connection via shared RedisProvider."""
    from app.infrastructure.cache.redis_provider import redis_provider
    return redis_provider.health_check()


def run_full_diagnostics() -> Dict[str, Any]:
    """Run all checks and return report."""
    return {
        "timestamp": os.getenv("VERCEL_DEPLOYMENT_ID", "local"),
        "environment": check_environment(),
        "database": check_database(),
        "redis": check_redis(),
    }


def log_startup_report():
    """Print diagnostics to stdout for Vercel Logs."""
    try:
        report = run_full_diagnostics()
        logger.info(f"🔍 [DIAGNOSTICS] REPORT: {report}")
    except Exception as e:
        logger.exception(f"⚠️ [DIAGNOSTICS] FAILED TO RUN: {e}")
