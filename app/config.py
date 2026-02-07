# =================================================================
# CONFIG.PY - Configuración centralizada con validación (Pydantic)
# Jorge Aguirre Flores Web
# =================================================================
import os
from typing import Optional, List, Union, Any
import logging
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Selective dotenv loading for local development only
if not os.getenv("VERCEL"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración centralizada del sistema con validación"""
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Meta Ads (Pixel + CAPI)
    META_PIXEL_ID: str = ""
    META_ACCESS_TOKEN: Optional[str] = None
    META_API_VERSION: str = "v21.0"
    TEST_EVENT_CODE: Optional[str] = None
    META_SANDBOX_MODE: bool = False # 🛡️ True = No enviar eventos reales a Meta
    
    # AI Brain (Gemini)
    GOOGLE_API_KEY: Optional[str] = None

    # Observability
    SENTRY_DSN: Optional[str] = None
    
    # =================================================================
    # 🚩 FEATURE FLAGS (Control via Vercel Environment Variables)
    # =================================================================
    # These are simple on/off switches you can toggle in Vercel Dashboard
    # without needing external feature flag providers.
    
    # Marketing & UX
    FLAG_SHOW_TESTIMONIALS: bool = True      # Show/hide testimonials section
    FLAG_SHOW_GALLERY: bool = True           # Show/hide gallery section
    FLAG_ENABLE_CHAT_WIDGET: bool = False    # Enable floating chat widget
    
    # A/B Testing (Simple)
    FLAG_CTA_VARIANT: str = "whatsapp"       # "whatsapp" | "form" | "call"
    FLAG_HERO_STYLE: str = "premium"         # "premium" | "minimal" | "video"
    
    # Tracking & Analytics
    FLAG_META_TRACKING: bool = True          # Master switch for Meta CAPI
    FLAG_GOOGLE_ANALYTICS: bool = True       # Master switch for GA4
    FLAG_HEATMAP_ENABLED: bool = False       # Enable heatmap tracking
    
    # Maintenance Mode
    FLAG_MAINTENANCE_MODE: bool = False      # Show maintenance page
    FLAG_BOOKING_ENABLED: bool = True        # Allow new bookings
    
    # Security: CORS Origins (Loaded manually to avoid Pydantic auto-parsing bugs)
    CORS_ALLOWED_ORIGINS: List[str] = [
        "https://jorgeaguirreflores.com",
        "https://www.jorgeaguirreflores.com",
        "https://jorge-aguirre-web.onrender.com",
        "https://jorge-web-ashen.vercel.app",
        "https://*.vercel.app",
        "http://localhost:8000",
        "http://localhost:5678"
    ]
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: Optional[str] = None
    
    # Celery & Redis
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis_evolution:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis_evolution:6379/1")
    CELERY_TASK_ALWAYS_EAGER: bool = False # Default to False, override via env var
    
    # Admin Panel
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "Andromeda2025")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # WhatsApp (Click Tracking Only)
    WHATSAPP_NUMBER: str = "59164714751"

    # =================================================================
    # 🚀 ELITE TRACKING INFRASTRUCTURE
    # =================================================================
    
    # Upstash Redis (Serverless Cache - for Event Deduplication)
    # Get credentials at: https://upstash.com
    UPSTASH_REDIS_REST_URL: Optional[str] = os.getenv("UPSTASH_REDIS_REST_URL")
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    # Microsoft Clarity (Free Heatmaps & Session Recordings)
    # Get project ID at: https://clarity.microsoft.com
    CLARITY_PROJECT_ID: Optional[str] = None
    
    # Cloudflare (If using Zaraz for ad-blocker bypass)
    CLOUDFLARE_ZONE_ID: Optional[str] = None
    TURNSTILE_SECRET_KEY: Optional[str] = None
    TURNSTILE_SITE_KEY: str = "0x4AAAAAAA8Cqg0HkqG6Xq5j"  # Default to visible key if not provided

    # RudderStack (CDP)
    # Get Write Key at: https://rudderstack.com
    RUDDERSTACK_WRITE_KEY: Optional[str] = None
    RUDDERSTACK_DATA_PLANE_URL: Optional[str] = None
    
    # Google One Tap (Identity Resolution)
    # Get Client ID at: https://console.cloud.google.com/apis/credentials
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
            # 🛡️ INFRASTRUCTURE SAFETY CHECK (Silicon Valley Standard)
            # Prevent "Connection Bomb" in Serverless (Vercel)
            is_prod = os.getenv("VERCEL") or os.getenv("RENDER")
            if is_prod and ":5432" in self.DATABASE_URL:
                 logger.warning("🔥 CRITICAL ARCHITECTURE WARNING: You are using Port 5432 (Session Mode) in Serverless.")
                 logger.warning("👉 PLEASE SWITCH TO PORT 6543 (Transaction Pooler) to avoid connection limits.")
                 # We don't raise error to avoid hard crash, but we scream in logs.
            
            if is_prod and "pgbouncer=true" not in self.DATABASE_URL:
                 logger.warning("⚠️ PERFORMANCE TIP: Add '?pgbouncer=true' to your DATABASE_URL for stability.")

        logger.info("✅ Configuración cargada correctamente")
    
    @property
    def meta_api_url(self) -> str:
        """URL completa para Meta CAPI"""
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.META_PIXEL_ID}/events"
    
    @property
    def whatsapp_url(self) -> str:
        """URL de WhatsApp con número"""
        return f"https://wa.me/{self.WHATSAPP_NUMBER}"


# Singleton de configuración
settings = Settings()

# 🛡️ MANUAL CONFIG PATCH: Pydantic-settings tries to JSON-decode "complex" field names.
# We bypass this by loading the env var manually into our internal field.
_env_origins = os.getenv("BACKEND_CORS_ORIGINS")
if _env_origins:
    settings.CORS_ALLOWED_ORIGINS = [i.strip() for i in _env_origins.split(",") if i.strip()]

settings.validate_critical()
