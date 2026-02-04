# =================================================================
# HEALTH.PY - Health Check Endpoints
# Jorge Aguirre Flores Web
# =================================================================
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

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


@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    """Ping simple para monitoreo básico"""
    return "pong"
