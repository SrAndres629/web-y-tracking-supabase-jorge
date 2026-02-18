# =================================================================
# CONFIG.PY - Configuración centralizada con validación (Pydantic)
# Jorge Aguirre Flores Web
# =================================================================
import logging
import os
from typing import Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ✅ Versión centralizada
from app.version import VERSION

__version__ = VERSION

# Selective dotenv loading for local development only
if not os.getenv("VERCEL"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _resolve_templates_dirs() -> List[str]:
    """Resolve template paths using api/templates as single source of truth."""
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_file_dir)

    candidates = []
    if os.getenv("VERCEL"):
        candidates.append("/var/task/api/templates")
        candidates.append("/var/task/templates")
        candidates.append(os.path.join(os.getcwd(), "api", "templates"))

    candidates.append(os.path.join(project_root, "api", "templates"))
    candidates.append(os.path.join(os.getcwd(), "api", "templates"))

    # Keep only existing directories plus serverless runtime paths on Vercel.
    is_vercel = bool(os.getenv("VERCEL"))
    valid_paths = []
    for p in candidates:
        if os.path.isdir(p) or (is_vercel and p.startswith("/var/task")):
            if p not in valid_paths:
                valid_paths.append(p)

    if not valid_paths:
        valid_paths = [os.path.join(project_root, "api", "templates")]

    logger.info("🚀 TEMPLATE RESOLUTION: Found %d potential paths", len(valid_paths))
    return valid_paths


def _resolve_static_dir() -> str:
    """Resolve static files directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.getenv("VERCEL"):
        return os.path.join(os.getcwd(), "static")
    return os.path.join(base_dir, "static")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 📂 PHYSICAL PATHS (Serverless Hardening)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMPLATES_DIRS: List[str] = _resolve_templates_dirs()
    TEMPLATES_DIR: str = TEMPLATES_DIRS[0] if TEMPLATES_DIRS else ""
    STATIC_DIR: str = _resolve_static_dir()

    # Meta Ads (Pixel + CAPI)
    META_PIXEL_ID: str = ""
    META_ACCESS_TOKEN: Optional[str] = None
    META_API_VERSION: str = "v21.0"
    TEST_EVENT_CODE: Optional[str] = None
    META_SANDBOX_MODE: bool = False  # 🛡️ True = No enviar eventos reales a Meta

    # AI Brain (Gemini)
    GOOGLE_API_KEY: Optional[str] = None

    # LLM Configuration
    GROQ_API_KEY: Optional[str] = None

    # Observability
    SENTRY_DSN: Optional[str] = None

    # =================================================================
    # 🚩 FEATURE FLAGS (Control via Vercel Environment Variables)
    # =================================================================
    # Marketing & UX
    FLAG_SHOW_TESTIMONIALS: bool = True  # Show/hide testimonials section
    FLAG_SHOW_GALLERY: bool = True  # Show/hide gallery section
    FLAG_ENABLE_CHAT_WIDGET: bool = False  # Enable floating chat widget

    # A/B Testing (Simple)
    FLAG_CTA_VARIANT: str = "whatsapp"  # "whatsapp" | "form" | "call"
    FLAG_HERO_STYLE: str = "premium"  # "premium" | "minimal" | "video"

    # Tracking & Analytics
    FLAG_META_TRACKING: bool = True  # Master switch for Meta CAPI
    FLAG_HEATMAP_ENABLED: bool = False  # Enable heatmap tracking

    # Maintenance Mode
    FLAG_MAINTENANCE_MODE: bool = False  # Show maintenance page
    FLAG_BOOKING_ENABLED: bool = True  # Allow new bookings

    # Multi-tenant controls
    ALLOWED_TENANTS: List[str] = Field(
        default_factory=lambda: ["default"],
        alias="ALLOWED_TENANTS",
        description="Comma separated tenant IDs allowed to use the API",
    )
    DEFAULT_TENANT: str = Field(
        default="default",
        alias="DEFAULT_TENANT",
        description="Fallback tenant ID when no header is supplied",
    )

    # Security: CORS Origins
    CORS_ALLOWED_ORIGINS: List[str] = [
        "https://jorgeaguirreflores.com",
        "https://www.jorgeaguirreflores.com",
        "https://jorge-aguirre-web.onrender.com",
        "https://jorge-web-ashen.vercel.app",
        "https://*.vercel.app",
        "http://localhost:8000",
        "http://localhost:5678",
    ]

    # Database (Supabase PostgreSQL)
    DATABASE_URL: Optional[str] = None

    # Celery & Redis
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL", "redis://redis_evolution:6379/1"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis_evolution:6379/1"
    )
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key-change-me")
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "Andromeda2025")

    # Server
    HOST: str = "0.0.0.0"  # nosec B104
    PORT: int = 8000

    # WhatsApp (Click Tracking Only)
    WHATSAPP_NUMBER: str = "59164714751"

    # Upstash Redis (Serverless Cache - for Event Deduplication)
    UPSTASH_REDIS_REST_URL: Optional[str] = os.getenv("UPSTASH_REDIS_REST_URL")
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = os.getenv("UPSTASH_REDIS_REST_TOKEN")

    # QStash (Background Tasks)
    QSTASH_URL: Optional[str] = None
    QSTASH_TOKEN: Optional[str] = None
    QSTASH_CURRENT_SIGNING_KEY: Optional[str] = None
    QSTASH_NEXT_SIGNING_KEY: Optional[str] = None

    # n8n Webhook (Optional)
    N8N_WEBHOOK_URL: Optional[str] = None

    # Microsoft Clarity
    CLARITY_PROJECT_ID: Optional[str] = None

    # Cloudflare
    CLOUDFLARE_ZONE_ID: Optional[str] = os.getenv("CLOUDFLARE_ZONE_ID")
    CLOUDFLARE_EMAIL: Optional[str] = os.getenv("CLOUDFLARE_EMAIL")
    CLOUDFLARE_API_KEY: Optional[str] = os.getenv("CLOUDFLARE_API_KEY")
    TURNSTILE_SECRET_KEY: Optional[str] = None
    TURNSTILE_SITE_KEY: str = "0x4AAAAAAA8Cqg0HkqG6Xq5j"

    # RudderStack (CDP)
    RUDDERSTACK_WRITE_KEY: Optional[str] = None
    RUDDERSTACK_DATA_PLANE_URL: Optional[str] = None

    # Google One Tap
    GOOGLE_CLIENT_ID: Optional[str] = None

    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is properly configured"""
        return bool(self.UPSTASH_REDIS_REST_URL and self.UPSTASH_REDIS_REST_TOKEN)

    @property
    def rudderstack_enabled(self) -> bool:
        """Check if RudderStack is properly configured"""
        return bool(self.RUDDERSTACK_WRITE_KEY and self.RUDDERSTACK_DATA_PLANE_URL)

    def validate_critical(self):
        """Valida configuración crítica"""
        if not self.META_PIXEL_ID:
            logger.warning("⚠️ META_PIXEL_ID no configurado")
        if not self.META_ACCESS_TOKEN:
            logger.warning("⚠️ META_ACCESS_TOKEN no configurado")
        if not self.DATABASE_URL:
            logger.info("ℹ️ DATABASE_URL no configurado - DB deshabilitada")
        else:
            is_prod = os.getenv("VERCEL") or os.getenv("RENDER")
            if is_prod and ":5432" in self.DATABASE_URL:
                logger.warning("🔥 CRITICAL ARCHITECTURE WARNING: Port 5432 In Use.")
                logger.warning("👉 SWITCH TO PORT 6543 for Pooling.")

            if is_prod and "pgbouncer=true" not in self.DATABASE_URL:
                logger.warning("⚠️ TIP: Add '?pgbouncer=true' to URL.")

        logger.info("✅ Configuración cargada correctamente")

    @property
    def meta_api_url(self) -> str:
        """URL completa para Meta CAPI"""
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.META_PIXEL_ID}/events"

    @property
    def whatsapp_url(self) -> str:
        """URL de WhatsApp con número"""
        return f"https://wa.me/{self.WHATSAPP_NUMBER}"

    # =================================================================
    # EXTERNAL INTEGRATIONS
    # =================================================================
    EXTERNAL_API_KEYS: Dict[str, Optional[str]] = Field(default_factory=dict)

    @field_validator("ALLOWED_TENANTS", mode="before")
    @classmethod
    def _normalize_tenants(cls, v):
        if isinstance(v, str):
            cleaned = [item.strip() for item in v.split(",") if item.strip()]
            return cleaned or ["default"]
        if isinstance(v, (list, tuple)):
            return [item for item in v if isinstance(item, str) and item.strip()]
        return ["default"]

    @property
    def tenant_list(self) -> List[str]:
        """List of allowed tenants."""
        tenants = []
        for tenant in self.ALLOWED_TENANTS:
            if tenant not in tenants:
                tenants.append(tenant)
        if self.DEFAULT_TENANT not in tenants:
            tenants.append(self.DEFAULT_TENANT)
        return tenants

    def resolve_tenant(self, candidate: Optional[str]) -> str:
        """Resolve tenant ID with fallback."""
        if not candidate:
            return self.DEFAULT_TENANT

        candidate = candidate.strip()
        if candidate in self.tenant_list:
            return candidate

        logger.warning(
            "⚠️ Tenant '%s' no permitido. Forzando '%s'.",
            candidate,
            self.DEFAULT_TENANT,
        )
        return self.DEFAULT_TENANT

    def is_tenant_allowed(self, tenant_id: Optional[str]) -> bool:
        """Check if tenant is allowed."""
        return bool(tenant_id) and tenant_id in self.tenant_list


# Singleton de configuración
settings = Settings()

# 🛡️ MANUAL CONFIG PATCH: CORS Origins
_env_origins = os.getenv("BACKEND_CORS_ORIGINS")
if _env_origins:
    settings.CORS_ALLOWED_ORIGINS = [
        i.strip() for i in _env_origins.split(",") if i.strip()
    ]

settings.validate_critical()
