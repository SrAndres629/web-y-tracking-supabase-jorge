# DIAGNOSTIC BOOTLOADER v2
import sys
import traceback

# 1. Try to load dependencies
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
    LOAD_ERROR = f"{str(e)}\n{traceback.format_exc()}"

# 3. Decision Logic
if not LOAD_ERROR and app and HAS_MANGUM:
    # SUCCESS: Normal Operation
    handler = Mangum(app)
else:
    # FAILURE: Fallback Mode
    fallback = FastAPI()
    
    @fallback.get("/{path:path}")
    async def debug_catch_all(path: str):
        return {
            "status": "BOOT_FAILURE",
            "has_mangum": HAS_MANGUM,
            "python_version": sys.version,
            "error": LOAD_ERROR or "Unknown Error (App is None)",
            "path": sys.path
        }
    
    if HAS_MANGUM:
        handler = Mangum(fallback)
    else:
        # If Mangum is missing, we can't do much on Vercel, 
        # but standard Vercel Python runtime might handle a simple WSGI app catchall? 
        # Actually Vercel expects 'handler' or 'app' to be an object it can invoke.
        # Let's hope Mangum is there (it should be).
        raise RuntimeError(f"CRITICAL: Mangum Missing. {LOAD_ERROR}")
