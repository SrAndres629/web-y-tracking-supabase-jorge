
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from app.domain.services.client_service import ClientService

logger = logging.getLogger(__name__)

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Paths that don't require API Key (e.g. public site, health)
        public_paths = ["/", "/health", "/static", "/tracking-motor", "/favicon.ico"]
        if request.url.path in public_paths or request.url.path.startswith("/static"):
             return await call_next(request)
        
        # Admin paths might have their own auth, skipping for now
        if request.url.path.startswith("/admin"):
             return await call_next(request)

        # Legacy routes or special hooks
        if request.url.path.startswith("/hooks"):
             return await call_next(request)

        # Required for /track/* routes
        if request.url.path.startswith("/track"):
            api_key = request.headers.get("X-API-Key")
            
            # For backward compatibility with the existing site, we might allow a "internal" bypass
            # or check for a default internal key.
            if not api_key:
                # Check for internal session or referrer? 
                # For now, if no API key, we'll try to use the default internal settings
                # as a fallback to not break jorgeaguirreflores.com
                request.state.client = None # Means use internal defaults
                return await call_next(request)
            
            client = ClientService.get_client_by_api_key(api_key)
            if not client:
                return JSONResponse(
                    status_code=401,
                    content={"status": "error", "message": "Invalid API Key"}
                )
            
            request.state.client = client
            logger.info(f"🔑 Authenticated client: {client['name']} ({client['plan']})")
        
        return await call_next(request)
