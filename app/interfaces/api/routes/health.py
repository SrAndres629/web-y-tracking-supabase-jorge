# =================================================================
# HEALTH.PY - Health Check Endpoints (API Interface)
# Jorge Aguirre Flores Web
# =================================================================
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import traceback

from app.database import check_connection
from app.config import settings

router = APIRouter(tags=["Health"])


@router.head("/health")
async def head_health_check():
    """HEAD check for UptimeRobot"""
    return JSONResponse({"status": "healthy"})


@router.get("/health")
async def health_check(request: Request):
    """
    Health check completo con verificación de base de datos
    Usado por UptimeRobot, Render, etc.
    """
    db_status = "connected" if check_connection() else "not configured"
    
    # Check optional integrations
    integrations = []
    if settings.redis_enabled:
        integrations.append("redis_upstash")
    if settings.CLARITY_PROJECT_ID:
        integrations.append("clarity")
    if settings.rudderstack_enabled:
        integrations.append("rudderstack")
        
    # Check Cloudflare
    if request.headers.get("cf-ray"):
        integrations.append("cloudflare_proxy")
        
    if settings.SENTRY_DSN:
        integrations.append("sentry")

    
    return JSONResponse({
        "status": "healthy",
        "database": db_status,
        "integrations": integrations,
        "timestamp": datetime.now().isoformat(),
        "service": "Jorge Aguirre Flores Web"
    })


@router.get("/health/diagnostics")
async def health_diagnostics_full(request: Request):
    """
    Reporte de diagnóstico completo (sistema, DB, Redis, env)
    """
    from app.diagnostics import run_full_diagnostics
    report = run_full_diagnostics()
    return JSONResponse(report)


@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    """Ping simple para monitoreo básico"""
    return "pong"


@router.get("/__prewarm_debug")
async def prewarm_debug(request: Request):
    """
    Endpoint de diagnóstico forense para prewarm.
    Devuelve rutas de templates y errores completos.
    """
    header_key = request.headers.get("x-prewarm-debug")
    query_key = request.query_params.get("__debug_key")
    if header_key is None and query_key is None:
        return JSONResponse({"status": "error", "message": "Not Found"}, status_code=404)

    candidates = [
        settings.TEMPLATES_DIR,
        os.path.join(os.getcwd(), "api", "templates"),
        os.path.join(os.getcwd(), "templates"),
        "/var/task/api/templates",
        "/var/task/templates",
        "api/templates",
    ]
    probe = "pages/public/home.html"
    found = []
    checked = []
    for base in candidates:
        if not base:
            continue
        checked.append(base)
        try:
            path = os.path.join(base, probe)
            if os.path.exists(path):
                found.append(path)
        except Exception:
            pass

    if found:
        return JSONResponse({
            "status": "ok",
            "probe": probe,
            "found": found,
            "cwd": os.getcwd(),
            "checked": checked,
        })

    return JSONResponse({
        "status": "error",
        "message": "Template not found",
        "probe": probe,
        "cwd": os.getcwd(),
        "checked": checked,
        "traceback": traceback.format_exc(),
    }, status_code=500)
