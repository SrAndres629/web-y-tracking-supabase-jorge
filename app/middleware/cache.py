from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


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
            if any(
                path.endswith(ext)
                for ext in [
                    ".css",
                    ".js",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".svg",
                    ".woff",
                    ".woff2",
                ]
            ):
                response.headers["Cache-Control"] = (
                    "public, max-age=2592000, stale-while-revalidate=86400"
                )

        # 2. Cache for Dynamic Pages (Only if not already set by route handler)
        elif not path.startswith("/static") and response.status_code == 200:
            if "text/html" in response.headers.get("content-type", ""):
                # Only set default headers if Cache-Control is not already set
                if "Cache-Control" not in response.headers:
                    response.headers["Cache-Control"] = (
                        "public, max-age=3600, stale-while-revalidate=86400"
                    )
                    response.headers["CDN-Cache-Control"] = "public, max-age=3600"

        return response
