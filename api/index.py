import sys
import os

# 1. Force absolute paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 2. Diagnostics: Catch import errors immediately
try:
    from main import app
except Exception as e:
    # 💥 CRITICAL BOOT FAILURE
    # This block renders the red/black diagnostic screen if main.py fails using the existing logic in app/diagnostics.py
    import traceback
    error_trace = traceback.format_exc()
    
    # Try to load our custom diagnostic renderer
    try:
        from app.diagnostics import run_full_diagnostics
        report = run_full_diagnostics()
    except ImportError:
        report = {"status": "Fatal Diagnostic Failure", "error": str(e)}

    # Fallback generic WSGI handler to show the error
    def app(environ, start_response):
        status = '503 Service Unavailable'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        # HTML Template matching the user's description (Black/Red)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>💥 CRITICAL BOOT FAILURE</title>
            <style>
                body {{ background: #000; color: #fff; font-family: monospace; padding: 2rem; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #ff3333; border-bottom: 2px solid #ff3333; padding-bottom: 1rem; }}
                .box {{ background: #111; border: 1px solid #333; padding: 1rem; margin-top: 1rem; border-radius: 5px; }}
                .error {{ color: #ff9999; white-space: pre-wrap; }}
                .hint {{ color: #888; margin-top: 1rem; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💥 CRITICAL BOOT FAILURE</h1>
                <p>The application failed to start. Vercel is running, but your code crashed.</p>
                
                <div class="box">
                    <h3>Error Traceback:</h3>
                    <div class="error">{error_trace}</div>
                </div>

                <div class="box">
                    <h3>Diagnostics Report:</h3>
                    <pre>{report}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
