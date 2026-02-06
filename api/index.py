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
    handler = Mangum(main_app, lifespan="off")
except Exception as e:
    LOAD_ERROR = f"{str(e)}\n{traceback.format_exc()}"
    print(f"🔥 [BOOT] CRITICAL FAILURE: {LOAD_ERROR}")
    
    # Emergency Fallback Handler
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "BOOT_FAILURE",
                "message": "Crash during application import",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "python": sys.version,
                "path": sys.path
            })
        }


