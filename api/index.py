# DIAGNOSTIC BOOTLOADER v3 (Unified Integration)
import sys
import traceback

# 0. Run Unified Diagnostics (Logs to Vercel Console)
try:
    # Diagnostic module is safe to import (lazy loads dependencies)
    from app.diagnostics import log_startup_report
    log_startup_report()
except ImportError:
    print("⚠️ [BOOT] Could not import app.diagnostics")
except Exception as e:
    print(f"⚠️ [BOOT] Diagnostics failed: {e}")

# 1. Try to load dependencies (Mangum)
try:
    from mangum import Mangum
    HAS_MANGUM = True
except ImportError:
    HAS_MANGUM = False
    Mangum = None

from fastapi import FastAPI

# 2. Try to load Main App
LOAD_ERROR = None
app = None
handler = None

try:
    from main import app as main_app
    app = main_app
except Exception as e:
    # Capture the full traceback for the JSON response
    LOAD_ERROR = f"{str(e)}\n{traceback.format_exc()}"
    print(f"🔥 [BOOT] CRITICAL APP LOAD FAILURE:\n{LOAD_ERROR}")

# 3. Decision Logic
if not LOAD_ERROR and app and HAS_MANGUM:
    # SUCCESS: Normal Operation
    # Wrap API for Vercel Serverless (AWS Lambda compatibility)
    handler = Mangum(app)
else:
    # FAILURE: Fallback Mode
    print("⚠️ [BOOT] Entering Fallback Mode")
    fallback = FastAPI()
    
    @fallback.get("/{path:path}")
    async def debug_catch_all(path: str):
        return {
            "status": "BOOT_FAILURE",
            "has_mangum": HAS_MANGUM,
            "python_version": sys.version,
            "error": LOAD_ERROR or "Unknown Error (App is None)",
            "path": sys.path,
            "env_check": "Check Vercel Logs for [DIAGNOSTICS] report"
        }
    
    if HAS_MANGUM:
        handler = Mangum(fallback)
    else:
        # Emergency raw handler if Mangum is gone (unlikely on Vercel Python runtime)
        raise RuntimeError(f"CRITICAL: Mangum Missing & App Failed. {LOAD_ERROR}")
