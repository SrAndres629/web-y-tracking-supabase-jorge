import os
import sys
import logging
from typing import Dict, Any, List

# No top-level imports that might crash if dependencies are missing
# Import lazily inside functions

logger = logging.getLogger("diagnostics")

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
            "PYTHONPATH": os.getenv("PYTHONPATH", "unset")
        }
    }

def check_database() -> Dict[str, Any]:
    """Verify Supabase connection"""
    status = {"status": "unknown", "backend": "none", "details": ""}
    try:
        from app.database import init_pool, get_cursor, BACKEND
        from app.config import settings
        
        # Check if URL is placeholder
        if settings.DATABASE_URL == "REQUIRED_IN_VERCEL":
            return {"status": "skipped", "details": "Local placeholder detected"}

        if not settings.DATABASE_URL:
             return {"status": "failed", "details": "DATABASE_URL not set"}

        # Attempt Init
        if init_pool():
            status["backend"] = BACKEND
            with get_cursor() as cur:
                cur.execute("SELECT version();")
                v = cur.fetchone()[0]
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
        from app.cache import redis_health_check
        status = redis_health_check()
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
        "redis": check_redis()
    }

def log_startup_report():
    """Print diagnostics to stdout for Vercel Logs"""
    try:
        report = run_full_diagnostics()
        print(f"🔍 [DIAGNOSTICS] REPORT: {report}")
    except Exception as e:
        print(f"⚠️ [DIAGNOSTICS] FAILED TO RUN: {e}")
