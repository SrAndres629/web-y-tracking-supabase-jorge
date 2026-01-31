# =================================================================
# HEALTH.PY - Health Check Endpoints
# Jorge Aguirre Flores Web
# =================================================================
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from app.database import check_connection

router = APIRouter(tags=["Health"])


@router.head("/health")
async def head_health_check():
    """HEAD check for UptimeRobot"""
    return JSONResponse({"status": "healthy"})


@router.get("/health")
async def health_check():
    """
    Health check completo con verificación de base de datos
    Usado por UptimeRobot, Render, etc.
    """
    db_status = "connected" if check_connection() else "not configured"
    
    return JSONResponse({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "service": "Jorge Aguirre Flores Web"
    })


@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    """Ping simple para monitoreo básico"""
    return "pong"
