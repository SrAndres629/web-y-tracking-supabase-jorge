# =================================================================
# MAIN.PY - Entry Point (Thin Wrapper)
# Jorge Aguirre Flores Web
# =================================================================
# 
# Este archivo es un punto de entrada limpio que:
# 1. Configura la aplicación FastAPI
# 2. Monta los archivos estáticos
# 3. Incluye todos los routers modulares
# 4. Inicializa la base de datos
#
# La lógica de negocio está en el paquete app/
# =================================================================

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import logging
import gc
import os
import time

# Configuración de Logging prioritaria
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_sentry():
    """Lazy init for Sentry to avoid blocking the main thread during startup"""
    from app.config import settings
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )
            logger.info("🛡️ Sentry Monitoring Active")
        except ImportError:
            logger.warning("⚠️ Sentry not installed")

# Configurar logging (Ya configurado arriba, eliminado bloque duplicado)

# =================================================================
# EVENTOS DE CICLO DE VIDA
# =================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación con manejo de contexto"""
    # Startup - OPTIMIZED: No blocking DB init
    logger.info("🚀 Iniciando Jorge Aguirre Flores Web v2.1.1 (Extreme Performance Mode)")
    
    # DLQ disabled: retry_queue.py uses filesystem (incompatible with Vercel serverless)
    # TODO: Re-enable when migrated to Redis-backed retry queue
    logger.info("⚠️ DLQ disabled (serverless-incompatible filesystem writes)")
    
    # 1. Initialize Sentry (Parallelizable/Non-blocking)
    init_sentry()
    
    # 2. Warm CMS Cache (Zero-Latency Content)
    from app.services import ContentManager
    await ContentManager.warm_cache()
    
    # NOTE: Database connection is now LAZY (initialized on first request)
    logger.info("⚡ Cold Start Optimization: Database will connect on first request")
    
    from app.config import settings
    logger.info(f"📊 Meta Pixel ID: {settings.META_PIXEL_ID}")
    logger.info(f"🌐 Servidor listo en http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Deteniendo servidor...")
    gc.collect()  # Force garbage collection on shutdown


# =================================================================
# APLICACIÓN FASTAPI
# =================================================================

app = FastAPI(
    title="Jorge Aguirre Flores Web",
    description="Sitio web profesional con tracking Meta CAPI",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Middleware GZip para compresión (5x más rápido en móviles)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Middleware para Proxy/CDN (Cloudflare/Render)
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Middleware CORS (Seguridad: permitir solo dominios propios)
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: Server-Side Identity (AdBlocker Bypass)
from app.middleware.identity import ServerSideIdentityMiddleware
app.add_middleware(ServerSideIdentityMiddleware)

# Middleware: Early Hints Bridge (Cloudflare 103 Optimization)
from app.middleware.early_hints import EarlyHintsMiddleware
app.add_middleware(EarlyHintsMiddleware)

# Middleware: Security Shield (Phase 13.5)
from app.middleware.security import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# =================================================================
# SECURITY: RATE LIMITING (Redis-Backed)
# =================================================================
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =================================================================
# DEBUGGING: EXCEPTION HANDLERS
# =================================================================
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    """
    Production-safe error handler.
    Logs full diagnostics server-side but returns sanitized response to client.
    If a valid debug key is provided, return full traceback for prewarm diagnostics.
    """
    logger.exception(f"🔥 CRITICAL 500 on {request.url.path}: {exc}")

    debug_key = os.getenv("PREWARM_DEBUG_KEY") or os.getenv("DEBUG_DIAGNOSTIC_KEY")
    header_key = request.headers.get("x-prewarm-debug")
    query_key = request.query_params.get("__debug_key")
    debug_allowed = bool(debug_key and (header_key == debug_key or query_key == debug_key))

    if debug_allowed:
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

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
        }
    )

# Aplicar límite global (opcional, o por ruta)
# app.add_middleware(SlowAPIMiddleware)

# =================================================================
# ARCHIVOS ESTÁTICOS (ABSOLUTE PATH FIX)
# =================================================================

# Get absolute path to static folder (fixes Docker/Render path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =================================================================
# ROUTERS - LAZY LOADING
# =================================================================

# Páginas HTML
from app.routes import pages
app.include_router(pages.router)

# Tracking endpoints (/track-lead, /track-viewcontent)
from app.routes import tracking_routes
app.include_router(tracking_routes.router)

# Panel de administración (/admin/*)
from app.routes import admin
app.include_router(admin.router)

# Health checks (/health, /ping)
from app.routes import health
app.include_router(health.router)

# Identity Resolution (/api/identity/*)
from app.routes import identity_routes
app.include_router(identity_routes.router)

# Chat routes (Evolution/Natalia) moved to separate microservice

# SEO Routes (sitemap.xml, robots.txt)
from app.routes import seo
app.include_router(seo.router)


# =================================================================
# EVENTOS DE CICLO DE VIDA (Movido arriba para lifespan)
# =================================================================



# =================================================================
# ARRANQUE
# =================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Hot reload para desarrollo
    )
