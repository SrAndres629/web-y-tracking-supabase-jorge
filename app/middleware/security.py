from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import re

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    🛡️ SILICON VALLEY SECURITY SHIELD
    ---------------------------------
    Implements standard HTTP security headers to prevent:
    1. Clickjacking (X-Frame-Options)
    2. MIME Sniffing (X-Content-Type-Options)
    3. Man-in-the-Middle (HSTS)
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
        
        # 1. Force HTTPS (HSTS) - 1 Year Cache
        # Tells browser: "Never load this site over HTTP again"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # 2. Prevent Clickjacking
        # Tells browser: "Do not allow this site to be embedded in an iframe"
        # Exception: You might need to relax this for specific partners
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
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # 7. Content Security Policy (Report-Only to avoid breaking things)
        # This policy is a starting point. It allows inline scripts/styles and scripts 
        # from any source, which is not secure but allows us to get violation reports.
        # The 'report-uri' should be replaced with a real endpoint to collect reports.
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-src 'self' https:; "
            "report-uri /api/csp-violations;"
        )
        response.headers["Content-Security-Policy-Report-Only"] = csp_policy
        
        return response
