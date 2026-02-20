import logging
import os
import sys
from typing import Any, Dict

logger = logging.getLogger(__name__)

# No top-level imports that might crash if dependencies are missing
# Import lazily inside functions


def check_environment() -> Dict[str, Any]:
    """Audit environment variables and system info"""
    from app.config import settings

    # Mask secrets
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
    """Verify Supabase connection"""
    status = {"status": "unknown", "backend": "none", "details": ""}
    try:
        from app import database as legacy_database
        from app.config import settings

        # Check if URL is invalid stub
        if settings.DATABASE_URL == "STUB_FOR_VERCEL":
            return {"status": "skipped", "details": "INVALID_DATABASE_URL_STUB"}

        if not settings.DATABASE_URL:
            return {"status": "failed", "details": "DATABASE_URL not set"}

        if legacy_database.check_connection():
            status["backend"] = legacy_database.BACKEND
            with legacy_database.get_cursor() as cur:
                cur.execute("SELECT version();")
                row = cur.fetchone()
                v = row[0] if row else "Unknown"
                status["status"] = "ok"
                status["details"] = v
        else:
            status["status"] = "failed"
            status["details"] = "Could not initialize pool"

    except Exception as e:
        status["status"] = "error"
        status["details"] = str(e)

    return status


def check_redis() -> Dict[str, Any]:
    """Verify Redis connection"""
    status = {"status": "unknown"}
    try:
        from app.interfaces.api.dependencies import get_legacy_facade

        status = get_legacy_facade().redis_health_check()
    except Exception as e:
        status["status"] = "error"
        status["message"] = str(e)
    return status


def run_full_diagnostics() -> Dict[str, Any]:
    """Run all checks and return report"""
    return {
        "timestamp": os.getenv("VERCEL_DEPLOYMENT_ID", "local"),
        "environment": check_environment(),
        "database": check_database(),
        "redis": check_redis(),
    }


def log_startup_report():
    """Print diagnostics to stdout for Vercel Logs"""
    try:
        report = run_full_diagnostics()
        logger.info(f"🔍 [DIAGNOSTICS] REPORT: {report}")
    except Exception as e:
        logger.exception(f"⚠️ [DIAGNOSTICS] FAILED TO RUN: {e}")
