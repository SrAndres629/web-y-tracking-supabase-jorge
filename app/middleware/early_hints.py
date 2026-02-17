from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.interfaces.api.routes.pages import SYSTEM_VERSION
import logging

logger = logging.getLogger(__name__)

class EarlyHintsMiddleware(BaseHTTPMiddleware):
    """
    Senior Performance Middleware: Early Hints Bridge
    Adds 'Link' headers to HTML responses to trigger Cloudflare 103 Early Hints.
    This informs the browser of critical assets before the HTML is fully rendered.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only apply to successful HTML responses
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and "text/html" in content_type:
            links = [
                # 1. Main CSS (Versioned Dynamic)
                f'</static/dist/css/app.min.css?v={SYSTEM_VERSION}>; rel=preload; as=style',
                # 2. Critical Fonts (Google Fonts CSS)
                '<https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap>; rel=preload; as=style',
                # 3. Preconnect to Typography CDN
                '<https://fonts.gstatic.com>; rel=preconnect; crossorigin'
            ]
            
            # Combine into a single Link header (Standard practice)
            response.headers["Link"] = ", ".join(links)

            # 🛡️ SILICON VALLEY SYNCHRONICITY: Cache headers already set by route handler
            # Only set default if not already present (respect route handler overrides)
            if "Cache-Control" not in response.headers:
                response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
            
        return response
