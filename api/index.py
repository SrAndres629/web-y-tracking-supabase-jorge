from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os
import traceback

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Diagnostic v4 is ALIVE"}

@app.get("/health/diagnostics")
async def diagnostics():
    results = {}
    
    # Test Imports
    try:
        import psycopg2
        results["psycopg2"] = "ok"
    except Exception as e:
        results["psycopg2"] = str(e)

    try:
        import facebook_business
        results["facebook_business"] = "ok"
    except Exception as e:
        results["facebook_business"] = str(e)
        
    try:
        import rudder_sdk_python
        results["rudder_sdk_python"] = "ok"
    except Exception as e:
        results["rudder_sdk_python"] = str(e)

    try:
        from main import app as main_app
        results["main_app"] = "ok"
    except Exception as e:
        results["main_app_error"] = str(e)
        results["main_app_traceback"] = traceback.format_exc()

    return {
        "status": "diagnostic_complete",
        "results": results,
        "python": sys.version,
        "env": os.environ.get("ENVIRONMENT", "unknown")
    }

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return {"status": "catch_all", "path": full_path, "hint": "Try /health/diagnostics"}
