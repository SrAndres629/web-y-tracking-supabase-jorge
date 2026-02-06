# DIAGNOSTIC BOOTLOADER v4 (Zero-Dependency Isolation)
import sys
import traceback
import os
import json

# 1. Self-contained Log function (since print might be buffered)
def log_error(msg):
    print(msg, file=sys.stderr) # stderr often captured better
    print(msg, file=sys.stdout)

# 2. Try to load Mangum
try:
    from mangum import Mangum
    HAS_MANGUM = True
except ImportError:
    HAS_MANGUM = False
    Mangum = None

# 3. Environment Dump (Safe Mode)
ENV_DEBUG = {k: str(v)[:10] + "..." if "KEY" in k or "TOKEN" in k else v for k, v in os.environ.items()}

# 4. Try to load Main App
LOAD_ERROR = None
app = None
handler = None

try:
    from main import app as main_app
    app = main_app
except Exception as e:
    LOAD_ERROR = f"{str(e)}\n{traceback.format_exc()}"
    log_error(f"🔥 [BOOT] CRITICAL FAILURE: {LOAD_ERROR}")

# 5. Handler Logic
def fallback_handler(event, context):
    """Raw AWS Lambda Handler for extreme fallback"""
    body = {
        "status": "BOOT_FAILURE",
        "error": LOAD_ERROR or "Unknown",
        "has_mangum": HAS_MANGUM,
        "python": sys.version,
        "env_sample": ENV_DEBUG
    }
    return {
        "statusCode": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

if not LOAD_ERROR and app and HAS_MANGUM:
    handler = Mangum(app)
else:
    # Use fallback. If mangum exists, use it to wrap a dummy fastapi for nicer output
    if HAS_MANGUM:
        from fastapi import FastAPI
        fallback_app = FastAPI()
        @fallback_app.get("/{path:path}")
        async def catch_all(path: str):
            return json.loads(fallback_handler(None, None)["body"])
        handler = Mangum(fallback_app)
    else:
        # If no Mangum, use raw lambda handler (Vercel supports this too for Python)
        handler = fallback_handler
