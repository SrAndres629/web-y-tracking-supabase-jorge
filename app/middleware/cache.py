from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    ⚡ PERFORMANCE OPTIMIZATION (CPM REDUCTION)
    -------------------------------------------
    Sets Cache-Control headers for dynamic HTML pages only.
    Static assets are handled by vercel.json (max-age=31536000, immutable).
    DO NOT set Cache-Control for /static/* here — it would downgrade vercel.json's headers.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.url.path

        # Only set cache headers for dynamic HTML pages (not static assets)
        if not path.startswith("/static") and response.status_code == 200:
            if "text/html" in response.headers.get("content-type", ""):
                # Only set default headers if Cache-Control is not already set by route
                if "Cache-Control" not in response.headers:
                    response.headers["Cache-Control"] = (
                        "public, max-age=3600, stale-while-revalidate=86400"
                    )
                    response.headers["CDN-Cache-Control"] = "public, max-age=3600"

        return response
