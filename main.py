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
import mimetypes
import asyncio
import sys

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

# =================================================================
# EVENTOS DE CICLO DE VIDA
# =================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación con manejo de contexto"""
    # Startup - OPTIMIZED: No blocking DB init
    from app.version import VERSION
    logger.info(f"🚀 Iniciando Jorge Aguirre Flores Web v{VERSION} (Atomic Architecture Mode)")
    
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
        from app.services import ContentManager
        try:
            await asyncio.wait_for(ContentManager.warm_cache(), timeout=5)
        except asyncio.TimeoutError:
            logger.warning("⚠️ warm_cache timeout; continuing without warm cache")
        except Exception as e:
            logger.warning(f"⚠️ warm_cache failed: {e}")

        # NOTE: Database connection is now LAZY (initialized on first request)
        # but we trigger initial check in background
        from app.database import init_tables
        try:
            init_ok = await asyncio.wait_for(asyncio.to_thread(init_tables), timeout=5)
            if init_ok:
                logger.info("✅ Database initialized successfully")
            else:
                logger.error("❌ Database initialization reported failure")
        except asyncio.TimeoutError:
            logger.warning("⚠️ init_tables timeout; continuing with lazy DB init")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")

        logger.info("⚡ Cold Start Optimization: Database ready")
    else:
        logger.info("🧪 Test mode detected: skipping warm_cache and init_tables")
    
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

# Middleware: Cache Control (CPM Optimization)
from app.middleware.cache import CacheControlMiddleware
app.add_middleware(CacheControlMiddleware)

# Middleware: Multi-tenant Auth (MVP Phase 2)
from app.middleware.auth import APIKeyMiddleware
app.add_middleware(APIKeyMiddleware)

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

# =================================================================
# ARCHIVOS ESTÁTICOS (ABSOLUTE PATH FIX + MIME FIX)
# =================================================================

# Windows Fix: Ensure CSS/JS have correct MIME types
mimetypes.init()
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

# Get absolute path to static folder (fixes Docker/Render path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =================================================================
# ROUTERS - CLEAN ARCHITECTURE
# =================================================================

# Páginas HTML
from app.interfaces.api.routes import pages
app.include_router(pages.router)

# Tracking endpoints (/track/*)
from app.interfaces.api.routes import tracking
app.include_router(tracking.router)

# Panel de administración (/admin/*)
from app.interfaces.api.routes import admin
app.include_router(admin.router)

# Health checks (/health, /ping)
from app.interfaces.api.routes import health
app.include_router(health.router)

# Identity Resolution (/api/identity/*)
from app.interfaces.api.routes import identity
app.include_router(identity.router)

# SEO Routes (sitemap.xml, robots.txt)
from app.interfaces.api.routes import seo
app.include_router(seo.router)


# =================================================================
# ERROR HANDLERS (Clean Architecture)
# =================================================================
from app.interfaces.api.middleware.error_handler import setup_error_handlers
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
        reload=True  # Hot reload para desarrollo
    )
