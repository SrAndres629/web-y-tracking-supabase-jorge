import os
import sys
import traceback
from pathlib import Path

# Fix path resolution for imports
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

try:
    # 🚀 Intento de importación normal
    from main import app
except Exception as e:
    boot_error = str(e)
    # 🛡️ Fallback safe entry point en caso de crash total
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("boot_crash")
    logger.error("CRITICAL: Application failed to import in api/index.py: %s", boot_error)
    
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def crash_report(request: Request, path: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "boot_crash",
                "message": "The application failed to start (Boot Crash).",
                "error": boot_error,
                "path": path,
                "traceback": traceback.format_exc() if os.getenv("DEBUG") or os.getenv("VERCEL") else "Redacted"
            }
        )

# app es expuesto para Vercel/Serverless
__all__ = ["app"]
