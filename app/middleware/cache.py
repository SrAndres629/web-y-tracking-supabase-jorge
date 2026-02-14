from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    ⚡ PERFORMANCE OPTIMIZATION (CPM REDUCTION)
    -------------------------------------------
    Sets Cache-Control headers for static assets to improve page load speed
    and reduce server load. Faster sites get lower CPMs in Meta/Google Ads.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        path = request.url.path
        
        # 1. Very Aggressive Cache for Static Assets (CSS, JS, Images, Fonts)
        if path.startswith("/static/"):
            # 1 Year Cache (Immutable-like)
            # Use this only if you use content hashing in filenames
            # For now, 1 month is safe.
            if any(path.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".woff", ".woff2"]):
                response.headers["Cache-Control"] = "public, max-age=2592000, stale-while-revalidate=86400"
        
        # 2. No Cache for Dynamic Pages (Ensures fresh content)
        elif not path.startswith("/static") and response.status_code == 200:
            if "text/html" in response.headers.get("content-type", ""):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"

        return response
