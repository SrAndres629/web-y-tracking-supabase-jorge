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

import asyncio
import gc
import logging
import mimetypes
import os
import sys
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Internal Imports
from app.config import settings
from app.database import init_tables
from app.interfaces.api.middleware.error_handler import setup_error_handlers
from app.interfaces.api.routes import (
    admin,
    consent,
    health,
    identity,
    pages,
    seo,
    tracking,
    vision,
)
from app.limiter import limiter
from app.middleware.auth import APIKeyMiddleware
from app.middleware.cache import CacheControlMiddleware
from app.middleware.early_hints import EarlyHintsMiddleware
from app.middleware.identity import ServerSideIdentityMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.services import ContentManager
from app.version import VERSION

# Configuración de Logging prioritaria
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_sentry():
    """Lazy init for Sentry to avoid blocking the main thread during startup"""
    if settings.SENTRY_DSN:
        try:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )
            logger.info("🛡️ Sentry Monitoring Active")
        except ImportError:
            logger.warning("⚠️ Sentry not installed")


# =================================================================
# EVENTOS DE CICLO DE VIDA
# =================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación con manejo de contexto"""
    # Startup - OPTIMIZED: No blocking DB init

    logger.info(
        f"🚀 Iniciando Jorge Aguirre Flores Web v{VERSION} (Atomic Architecture Mode)"
    )

    is_test_mode = (
        os.getenv("PYTEST_CURRENT_TEST") is not None
        or os.getenv("AUDIT_MODE") == "1"
        or "PYTEST_VERSION" in os.environ
        or "pytest" in sys.modules
    )

    # 1. Initialize Sentry (Parallelizable/Non-blocking)
    init_sentry()

    # 2. Startup warmups only outside test/audit mode
    if not is_test_mode:
        try:
            await asyncio.wait_for(ContentManager.warm_cache(), timeout=5)
        except asyncio.TimeoutError:
            logger.warning("⚠️ warm_cache timeout; continuing without warm cache")
        except Exception as e:
            logger.warning(f"⚠️ warm_cache failed: {e}")

        # NOTE: Database connection is now LAZY (initialized on first request)
        # but we trigger initial check in background

        try:
            init_ok = await asyncio.wait_for(asyncio.to_thread(init_tables), timeout=5)
            if init_ok:
                logger.info("✅ Database initialized successfully")
            else:
                logger.error("❌ Database initialization reported failure")
        except asyncio.TimeoutError:
            logger.warning("⚠️ init_tables timeout; continuing with lazy DB init")
        except Exception as e:
            logger.exception(f"❌ Database initialization failed: {e}")

        logger.info("⚡ Cold Start Optimization: Database ready")
    else:
        logger.info("🧪 Test mode detected: skipping warm_cache and init_tables")

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
    description="Professional website with Meta CAPI tracking",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Middleware GZip para compresión (5x más rápido en móviles)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Middleware para Proxy/CDN (Cloudflare/Render)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Middleware CORS (Seguridad: permitir solo dominios propios)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: Server-Side Identity (AdBlocker Bypass)

app.add_middleware(ServerSideIdentityMiddleware)

# Middleware: Early Hints Bridge (Cloudflare 103 Optimization)

app.add_middleware(EarlyHintsMiddleware)

# Middleware: Security Shield (Phase 13.5)

app.add_middleware(SecurityHeadersMiddleware)

# Middleware: Cache Control (CPM Optimization)

app.add_middleware(CacheControlMiddleware)

# Middleware: Multi-tenant Auth (MVP Phase 2)

app.add_middleware(APIKeyMiddleware)

# =================================================================
# SECURITY: RATE LIMITING (Redis-Backed)
# =================================================================

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =================================================================
# DEBUGGING: EXCEPTION HANDLERS
# =================================================================

# =================================================================
# ARCHIVOS ESTÁTICOS (ABSOLUTE PATH FIX + MIME FIX)
# =================================================================

# Windows Fix: Ensure CSS/JS have correct MIME types
mimetypes.init()
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("image/webp", ".webp")

# Get absolute path to static folder (fixes Docker/Render path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =================================================================
# ROUTERS - CLEAN ARCHITECTURE
# =================================================================

# Páginas HTML

app.include_router(pages.router)

# Tracking endpoints (/track/*)

app.include_router(tracking.router)

# Panel de administración (/admin/*)

app.include_router(admin.router)

# Health checks (/health, /ping)

app.include_router(health.router)

# Identity Resolution (/api/identity/*)

app.include_router(identity.router)

# SEO Routes (sitemap.xml, robots.txt)

app.include_router(seo.router)

# Neuro-Vision Routes (Visual Cortex - NEXUS-7)

app.include_router(vision.router)
logger.info("🔮 Neuro-Vision routes mounted at /vision")

# Consent Management (GDPR/CCPA/LGPD)

app.include_router(consent.router)
logger.info("🛡️ Consent routes mounted at /consent")


# =================================================================
# ERROR HANDLERS (Clean Architecture)
# =================================================================

setup_error_handlers(app)
logger.info("✅ Error handlers configurados")


# =================================================================
# ARRANQUE
# =================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Hot reload para desarrollo
    )
