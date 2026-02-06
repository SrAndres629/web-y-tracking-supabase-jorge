# PRODUCTION HANDLER (with Diagnostic Safety)
import sys
import traceback
import os
import json

# DIAGNOSTIC BOOT
print("🚀 [BOOT] Starting Vercel Python Runtime...")
print(f"🐍 [BOOT] Python Version: {sys.version}")

try:
    print("📦 [BOOT] Importing Mangum...")
    from mangum import Mangum
    print("📦 [BOOT] Importing Main App...")
    from main import app as main_app
    print("✅ [BOOT] App Imported successfully.")
    
    # Production Handler
    app = Mangum(main_app, lifespan="off")
except Exception as e:
    LOAD_ERROR = f"{str(e)}\n{traceback.format_exc()}"
    print(f"🔥 [BOOT] CRITICAL FAILURE: {LOAD_ERROR}")
    
    # Emergency Fallback Handler (WSGI style for safety)
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        body = {
            "status": "BOOT_FAILURE",
            "message": "Crash during application import",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return [json.dumps(body).encode('utf-8')]



