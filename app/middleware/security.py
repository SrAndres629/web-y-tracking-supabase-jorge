from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import re

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    🛡️ SILICON VALLEY SECURITY SHIELD
    ---------------------------------
    Implements comprehensive HTTP security headers:
    1. Content Security Policy (CSP) - XSS protection
    2. HSTS - HTTPS enforcement with preload
    3. X-Frame-Options - Clickjacking protection
    4. X-Content-Type-Options - MIME sniffing protection
    5. Cross-Origin Opener Policy (COOP) - Origin isolation
    6. Referrer Policy - Privacy protection
    7. X-XSS-Protection - Legacy XSS protection
    8. Permissions Policy - Feature restrictions
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("uvicorn.error")
        # List of common bots/crawlers/scrapers
        self.bot_pattern = re.compile(
            r"(googlebot|bingbot|yandexbot|duckduckbot|slurp|baiduspider|facebookexternalhit|twitterbot|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest\/0\.|slackbot|vkShare|W3C_Validator|uptime|monitor|crawl|spider|scraper|bot)",
            re.IGNORECASE
        )

    async def dispatch(self, request: Request, call_next):
        # 🕵️ BOT DEFENSE: Mark request as human or bot
        user_agent = request.headers.get("user-agent", "")
        request.state.is_human = not bool(self.bot_pattern.search(user_agent))
        
        response = await call_next(request)
        
        # 1. Force HTTPS (HSTS) - 1 Year Cache with preload
        # Tells browser: "Never load this site over HTTP again"
        # includeSubDomains: Apply to all subdomains
        # preload: Allow browser vendors to hardcode this site as HTTPS-only
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # 2. Prevent Clickjacking
        # Tells browser: "Do not allow this site to be embedded in an iframe"
        response.headers["X-Frame-Options"] = "DENY"
        
        # 3. Prevent MIME Sniffing
        # Tells browser: "Trust the Content-Type header given by server"
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 4. Privacy: Referrer Policy
        # Only send origin (domain) when going to other HTTPS sites, full path internally
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 5. XSS Protection (Legacy but good defense in depth)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 6. Isolate the page from other origins (COOP)
        # Prevents window.opener attacks
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        
        # 7. Cross-Origin Resource Policy (CORP)
        # Protects against cross-origin information leaks
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # 8. Cross-Origin Embedder Policy (COEP)
        # Relaxed to credentialless to allow cross-origin resources (scripts/images) without CORP headers
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        
        # 9. Permissions Policy - Restrict browser features
        # Only allow necessary features
        response.headers["Permissions-Policy"] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # 10. Content Security Policy (CSP) - OPTIMIZED FOR GOOGLE & CLOUDFLARE
        # Prevents XSS while allowing necessary third-party services
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://*.googleapis.com https://*.gstatic.com https://cdnjs.cloudflare.com https://unpkg.com https://accounts.google.com https://connect.facebook.net https://static.cloudflareinsights.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://accounts.google.com; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self' https://*.upstash.io https://*.facebook.com https://*.googleapis.com https://accounts.google.com https://*.cloudflareinsights.com; "
            "frame-src 'self' https://challenges.cloudflare.com https://accounts.google.com https://*.facebook.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests;"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response
