"""
🚀 Main Entry Point - Enterprise Architecture.

Jorge Aguirre Flores Web v3.0.0
Clean Architecture con Domain-Driven Design.
"""

from __future__ import annotations

import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Añadir directorio raíz al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.infrastructure.config import get_settings
from app.interfaces.api.routes import tracking, pages

# Logging estructurado
try:
    import structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger()
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)


# Settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events.
    
    Startup: Warm caches, init Sentry
    Shutdown: Cleanup
    """
    # Startup
    logger.info(
        "🚀 Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment="production" if settings.server.is_production else "development",
    )
    
    # Log configuration status
    settings.log_status()
    
    # Init Sentry
    if settings.observability.sentry_enabled:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            sentry_sdk.init(
                dsn=settings.observability.sentry_dsn,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
            )
            logger.info("🛡️ Sentry initialized")
        except Exception as e:
            logger.warning("Failed to init Sentry", error=str(e))
    
    # Warm content cache
    try:
        from app.application.queries.get_content import GetContentQuery, GetContentHandler
        from app.interfaces.api.dependencies import get_content_cache
        
        handler = GetContentHandler(cache=get_content_cache())
        await handler.handle(GetContentQuery(key="services_config"))
        await handler.handle(GetContentQuery(key="contact_config"))
        logger.info("🔥 Content cache warmed")
    except Exception as e:
        logger.warning("Failed to warm cache", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Sitio web profesional con tracking Meta CAPI - Clean Architecture",
    version=settings.app_version,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if not settings.server.is_production else None,
    redoc_url="/redoc" if not settings.server.is_production else None,
)

# Middleware (order matters!)
# 1. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# 2. Proxy headers (Cloudflare/Render)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(tracking.router)

# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    }


# Run
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_new:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        workers=settings.server.workers if not settings.server.reload else 1,
    )
