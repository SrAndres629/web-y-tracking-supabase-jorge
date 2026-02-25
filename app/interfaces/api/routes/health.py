# =================================================================
# HEALTH.PY - Health Check Endpoints (API Interface)
# Jorge Aguirre Flores Web
# =================================================================
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.infrastructure.config.settings import settings
from app.interfaces.api.dependencies import get_legacy_facade

router = APIRouter(tags=["Health"])
legacy = get_legacy_facade()


@router.head("/health")
async def head_health_check():
    """HEAD check for UptimeRobot"""
    return JSONResponse({"status": "healthy"})


@router.get("/health")
@router.get("/healthcheck")
async def health_check(request: Request):
    """
    Health check completo con verificación de base de datos
    Usado por UptimeRobot, Render, etc.
    """
    is_test_mode = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("AUDIT_MODE") == "1"
    if is_test_mode:
        db_status = "skipped_in_test_mode"
    else:
        db_status = "connected" if legacy.check_connection() else "not configured"

    # Check optional integrations
    integrations = []
    if settings.redis_enabled:
        integrations.append("redis_upstash")
    if settings.CLARITY_PROJECT_ID:
        integrations.append("clarity")
    # Rudderstack removed

    # Check Cloudflare
    if request.headers.get("cf-ray"):
        integrations.append("cloudflare_proxy")

    if settings.SENTRY_DSN:
        integrations.append("sentry")

    return JSONResponse(
        {
            "status": "healthy",
            "database": db_status,
            "integrations": integrations,
            "integration_contract": settings.integration_contract(),
            "strict_startup": settings.CONFIG_STRICT_STARTUP,
            "timestamp": datetime.now().isoformat(),
            "service": "Jorge Aguirre Flores Web",
        }
    )


@router.get("/health/diagnostics")
async def health_diagnostics_full(request: Request):
    """
    Reporte de diagnóstico completo (sistema, DB, Redis, env)
    """
    from app.diagnostics import run_full_diagnostics

    report = run_full_diagnostics()
    return JSONResponse(report)


@router.get("/health/config")
async def health_config_contract():
    """Expose integration contract status for ops automation."""
    return JSONResponse(
        {
            "status": "ok",
            "strict_startup": settings.CONFIG_STRICT_STARTUP,
            "contract": settings.integration_contract(),
            "warnings": settings.validate_critical(),
        }
    )


@router.get("/health/assets")
async def health_assets():
    """
    Verifica que los assets críticos existan en runtime serverless.
    """
    project_root = Path(__file__).resolve().parents[4]
    static_root = Path(settings.STATIC_DIR)
    if not static_root.exists():
        static_root = project_root / "static"

    required = [
        static_root / "dist" / "css" / "app.min.css",
        static_root / "engines" / "tracking" / "index.js",
        static_root / "assets" / "images" / "branding" / "luxury_logo.svg",
    ]
    status = {
        str(path.relative_to(static_root) if path.exists() else path.name): path.exists()
        for path in required
    }

    all_ok = all(status.values())
    return JSONResponse(
        {
            "status": "ok" if all_ok else "error",
            "static_dir": str(static_root),
            "assets": status,
        },
        status_code=200 if all_ok else 500,
    )


@router.get("/ping", response_class=PlainTextResponse)
async def ping():
    """Ping simple para monitoreo básico"""
    return "pong"


def _prewarm_probe_payload(request: Request) -> dict:
    candidates = [
        settings.TEMPLATES_DIR,
        os.path.join(os.getcwd(), "api", "templates"),
        "/var/task/api/templates",
        "api/templates",
    ]
    probe = "pages/site/home.html"
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
    return {
        "probe": probe,
        "cwd": os.getcwd(),
        "checked": checked,
        "found": found,
    }


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

    payload = _prewarm_probe_payload(request)
    if payload["found"]:
        return JSONResponse({"status": "ok", **payload})
    return JSONResponse(
        {"status": "error", "message": "Template not found", **payload}, status_code=500
    )


@router.get("/health/prewarm")
async def prewarm_health(request: Request):
    """Health-style prewarm diagnostic endpoint."""
    header_key = request.headers.get("x-prewarm-debug")
    query_key = request.query_params.get("__debug_key")
    if header_key is None and query_key is None:
        return JSONResponse({"status": "error", "message": "Not Found"}, status_code=404)
    payload = _prewarm_probe_payload(request)
    if payload["found"]:
        return JSONResponse({"status": "ok", **payload})
    return JSONResponse(
        {"status": "error", "message": "Template not found", **payload}, status_code=500
    )
