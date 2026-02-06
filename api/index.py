import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# 1. Setup Path (Ensure root is in path)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    # 2. Try to import the main app
    from main import app as main_app
    app = main_app
    handler = app
except Exception as e:
    # 3. If it fails, create a diagnostic app
    app = FastAPI()
    
    @app.get("/{full_path:path}")
    async def crash_report(full_path: str):
        error_info = traceback.format_exc()
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: monospace; background: #1a1a1a; color: #ff5555; padding: 20px;">
                <h1 style="color: #E5C585;">💥 CRITICAL BOOT FAILURE</h1>
                <p>The application crashed during initialization.</p>
                <div style="background: #000; padding: 20px; border-radius: 8px; border: 1px solid #333;">
                    <pre>{error_info}</pre>
                </div>
                <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0;">
                <p style="color: #888;">Environment: {os.environ.get('VERCEL_ENV', 'unknown')}</p>
                <p style="color: #888;">Python: {sys.version}</p>
                <p style="color: #888;">CWD: {os.getcwd()}</p>
                <p style="color: #888;">Path: {sys.path}</p>
            </body>
        </html>
        """, status_code=500)
    
    handler = app
