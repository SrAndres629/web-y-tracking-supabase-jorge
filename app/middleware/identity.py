import time
import random
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class ServerSideIdentityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure Meta Tracking Cookies (_fbp, _fbc) 
    are present and set as HttpOnly to bypass AdBlockers.
    
    Format:
    - _fbp: fb.1.{timestamp}.{random_digits}
    - _fbc: fb.1.{timestamp}.{fbclid}
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # noqa: C901
        response = await call_next(request)
        
        # Skip for static files and API calls that are not page loads
        # (Though having them on API calls is fine, usually we want them on page loads)
        if request.url.path.startswith("/static") or request.url.path.startswith("/_vercel"):
            return response

        try:
            # 1. Handle Browser ID (_fbp)
            fbp = request.cookies.get("_fbp")
            if not fbp:
                # Generate new _fbp
                timestamp = int(time.time() * 1000)
                random_val = random.randint(1000000000, 9999999999)
                fbp = f"fb.1.{timestamp}.{random_val}"
                
                # Set HttpOnly cookie (2 years expiry)
                response.set_cookie(
                    key="_fbp",
                    value=fbp,
                    max_age=63072000,  # 2 years
                    httponly=True,
                    samesite="lax",
                    secure=True
                )
                # logger.debug(f"🍪 [Identity] Generated _fbp: {fbp}")

            # 2. Handle Click ID (_fbc) from fbclid query param
            fbclid = request.query_params.get("fbclid")
            if fbclid:
                # Always refresh _fbc if fbclid is present in URL
                # Format: fb.subdomain_index.creation_time.fbclid
                # subdomain_index is usually 1 for www or root
                creation_time = int(time.time() * 1000)
                fbc = f"fb.1.{creation_time}.{fbclid}"
                
                # Set HttpOnly cookie (90 days expiry)
                response.set_cookie(
                    key="_fbc",
                    value=fbc,
                    max_age=7776000,  # 90 days
                    httponly=True,
                    samesite="lax",
                    secure=True
                )
                logger.info(f"🍪 [Identity] Captured fbclid -> _fbc: {fbc}")

        except Exception as e:
            logger.error(f"❌ [Identity] Middleware Error: {e}")
            
        return response
