# =================================================================
# VISION.PY - Rutas para Neuro-Vision (Visual Cortex)
# Jorge Aguirre Flores Web - NEXUS-7 Integration
# =================================================================
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vision", tags=["neuro-vision"])

# Resolve paths for Neuro-Vision assets
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent  # Project root
VISION_DIR = BASE_DIR / ".ai" / "visuals"
VISION_TEMPLATES = VISION_DIR
VISION_STATIC = VISION_DIR / "static"


def get_vision_template(template_name: str) -> Path:
    """Get path to a vision template"""
    template_path = VISION_TEMPLATES / template_name
    if template_path.exists():
        return template_path
    # Fallback to v1
    fallback = VISION_TEMPLATES / "neuro_map.html"
    return fallback if fallback.exists() else template_path


@router.get("/", response_class=HTMLResponse)
async def neuro_vision_root(request: Request):
    """
    Neuro-Vision V2.0 - Cognitive Visual Cortex
    Visualizador 3D de arquitectura de código
    """
    template_path = get_vision_template("neuro_map_v2.html")

    if not template_path.exists():
        logger.error("❌ Neuro-Vision template not found at: %s", template_path)
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Neuro-Vision - Error</title></head>
            <body style="font-family: sans-serif; padding: 40px;">
                <h1>⚠️ Neuro-Vision Not Available</h1>
                <p>The visualization template is missing or not properly configured.</p>
                <p>Expected path: .ai/core/vision/templates/neuro_map_v2.html</p>
            </body>
            </html>
            """,
            status_code=503,
        )

    try:
        content = template_path.read_text(encoding="utf-8")

        # Inject cache-busting version
        from app.infrastructure.config.settings import settings

        content = content.replace("{{ system_version }}", settings.system_version)

        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Frame-Options": "SAMEORIGIN",
                "X-Content-Type-Options": "nosniff",
            },
        )
    except Exception:
        logger.exception("❌ Error serving Neuro-Vision")
        return HTMLResponse(content="<h1>Error serving Neuro-Vision</h1>", status_code=500)


@router.get("/v1", response_class=HTMLResponse)
async def neuro_vision_legacy(request: Request):
    """Legacy Neuro-Vision v1.0 (Original monolithic version)"""
    template_path = VISION_TEMPLATES / "neuro_map.html"

    if not template_path.exists():
        return HTMLResponse("Legacy template not found", status_code=404)

    content = template_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)


@router.get("/api/status")
async def vision_status():
    """Get Neuro-Vision system status"""
    status = {
        "version": "2.0.0",
        "template_v2_exists": (VISION_TEMPLATES / "neuro_map_v2.html").exists(),
        "template_v1_exists": (VISION_TEMPLATES / "neuro_map.html").exists(),
        "css_exists": (VISION_STATIC / "css" / "neuro_map.css").exists(),
        "js_exists": (VISION_STATIC / "js" / "neuro_core.js").exists(),
        "static_files": [],
    }

    # List available static files
    if VISION_STATIC.exists():
        for file_type in ["css", "js"]:
            type_dir = VISION_STATIC / file_type
            if type_dir.exists():
                for file in type_dir.iterdir():
                    if file.is_file():
                        status["static_files"].append(f"{file_type}/{file.name}")

    return status


# Static files endpoint for Neuro-Vision
# Note: In production, these should be served via CDN or nginx
@router.get("/static/{file_path:path}")
async def vision_static(file_path: str):
    """Serve Neuro-Vision static files (CSS, JS)"""
    # Security: Prevent directory traversal
    safe_path = Path(file_path).resolve()

    # Ensure the path is within the vision static directory
    try:
        full_path = (VISION_STATIC / safe_path).resolve()
        # Check if path is within allowed directory
        full_path.relative_to(VISION_STATIC.resolve())
    except (ValueError, RuntimeError):
        logger.warning(f"🚫 Attempted directory traversal: {file_path}")
        return HTMLResponse("Forbidden", status_code=403)

    if not full_path.exists() or not full_path.is_file():
        return HTMLResponse("Not found", status_code=404)

    # Determine content type
    content_type = "application/octet-stream"
    if file_path.endswith(".css"):
        content_type = "text/css"
    elif file_path.endswith(".js"):
        content_type = "application/javascript"
    elif file_path.endswith(".html"):
        content_type = "text/html"
    elif file_path.endswith(".json"):
        content_type = "application/json"

    return FileResponse(
        path=full_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )
