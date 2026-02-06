import os
import sys

# 🚀 SILICON VALLEY BOOTLOADER V3
# Ensures the app starts even if some optional dependencies are missing.

# 1. Setup Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    # 2. Import the main FastAPI app
    # This triggers the full application logic
    from main import app
except Exception as e:
    # 3. Fallback: Emergency Diagnostic App
    # If the main app fails to import (e.g. DB crash), we show a clean error page.
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    
    @app.get("/{full_path:path}")
    async def crash_report(full_path: str):
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: sans-serif; background: #0a0a0a; color: #fff; padding: 40px; text-align: center;">
                <h1 style="color: #E5C585;">🛠️ Sistema en Mantenimiento</h1>
                <p>El sitio está experimentando una pausa técnica breve.</p>
                <div style="background: #1a1a1a; padding: 20px; border-radius: 8px; text-align: left; max-width: 600px; margin: 40px auto; border: 1px solid #333;">
                    <code style="color: #ff5555;">ERROR: {str(e)}</code>
                </div>
                <button onclick="location.reload()" style="background: #C5A059; border: none; padding: 10px 20px; border-radius: 4px; color: #000; font-weight: bold; cursor: pointer;">
                    Reintentar Conexión
                </button>
            </body>
        </html>
        """, status_code=503)

# The handler must be named 'app' for Vercel
# Vercel's @vercel/python builder automatically detects and uses the FastAPI 'app' object.
