# PRODUCTION HANDLER (with Diagnostic Safety)
import sys
import traceback
import os
import json
from mangum import Mangum

# Load Main App
try:
    from main import app as main_app
    # Production Handler
    handler = Mangum(main_app, lifespan="off") # 'off' for serverless cold-start speed
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
                "error": LOAD_ERROR,
                "python": sys.version
            })
        }

