from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import traceback

app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "Direct FastAPI in api/index.py is working!",
        "python": sys.version
    }

@app.get("/health/diagnostics")
async def diagnostics():
    try:
        from main import app as main_app
        return {"status": "import_success", "main_app_found": True}
    except Exception as e:
        return {
            "status": "import_failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Fallback for all other routes to see if we can load the full app
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return {
        "status": "catch_all",
        "path": full_path,
        "hint": "Try /health to verify baseline."
    }
