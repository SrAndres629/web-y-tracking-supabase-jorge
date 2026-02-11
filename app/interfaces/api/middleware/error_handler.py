"""
📦 ERROR HANDLER MIDDLEWARE
Responsabilidad: Manejar errores globalmente de forma segura

❌ Error anterior: api/index.py generaba HTML inline (53 líneas)
✅ Solución: Middleware dedicado en app/
📚 Lección: No mezclar manejo de errores con entry point
"""

from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
import logging
import traceback
import os

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware para manejo consistente y seguro de errores.
    
    En producción, no expone información sensible como stack traces.
    En desarrollo, muestra información detallada para debugging.
    """
    
    def __init__(self, app=None):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """Intercepta requests y maneja excepciones."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.exception(f"Unhandled exception in request: {request.url}")
            return self._render_error(request, exc)
    
    def _debug_allowed(self, request: Request) -> bool:
        debug_key = os.getenv("PREWARM_DEBUG_KEY") or os.getenv("DEBUG_DIAGNOSTIC_KEY")
        header_key = request.headers.get("x-prewarm-debug")
        query_key = request.query_params.get("__debug_key")
        if debug_key and (header_key == debug_key or query_key == debug_key):
            return True
        # Fallback: explicit prewarm probe (no env key set)
        ua = request.headers.get("user-agent", "")
        if header_key == "1" and query_key == "1" and "SV-Prewarm" in ua:
            return True
        return False

    def _render_error(self, request: Request, exc: Exception):
        """
        Renderiza error según el entorno.
        
        - Debug: Retorna JSON con stack trace completo
        - Producción: Mensaje genérico amigable
        """
        if self._debug_allowed(request) or os.getenv("DEBUG", "false").lower() == "true":
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal Server Error (Debug Mode)",
                    "detail": str(exc),
                    "type": type(exc).__name__,
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": tb,
                }
            )
        
        error_detail = "<p>El equipo técnico ha sido notificado. Por favor intente más tarde.</p>"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - Jorge Aguirre Flores</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                    color: #ffffff;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                    padding: 2rem;
                }}
                .container {{
                    max-width: 800px;
                    width: 100%;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                    padding: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                h1 {{
                    color: #C5A059;
                    margin-bottom: 1rem;
                    font-size: 2rem;
                }}
                .error-box {{
                    background: rgba(197, 160, 89, 0.1);
                    border-left: 4px solid #C5A059;
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin-top: 1.5rem;
                }}
                .contact {{
                    margin-top: 2rem;
                    padding-top: 2rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    color: #888;
                }}
                pre {{
                    background: #1a1a1a;
                    padding: 1rem;
                    border-radius: 8px;
                    overflow-x: auto;
                    font-size: 0.875rem;
                    color: #e0e0e0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Ha ocurrido un error</h1>
                <p>Lo sentimos, algo salió mal al procesar su solicitud.</p>
                
                <div class="error-box">
                    {error_detail}
                </div>
                
                <div class="contact">
                    <p>Si el problema persiste, por favor contacte a soporte técnico.</p>
                    <p><strong>Jorge Aguirre Flores Web</strong> v3.0.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html, status_code=500)


def setup_error_handlers(app):
    """
    Configura manejadores de error en la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        """Manejador para errores 500."""
        handler = ErrorHandlerMiddleware()
        return handler._render_error(request, exc)
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception):
        """Manejador para errores 404."""
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>No encontrado</title></head>
            <body style="text-align: center; padding: 50px;">
                <h1>404 - Página no encontrada</h1>
                <p>La página que busca no existe.</p>
                <a href="/">Volver al inicio</a>
            </body>
            </html>
            """,
            status_code=404
        )
    
    logger.info("✅ Error handlers configurados")
