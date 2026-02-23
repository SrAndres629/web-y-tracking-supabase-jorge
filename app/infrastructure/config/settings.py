"""
⚙️ Enterprise Settings - Configuración centralizada con validación.

Basado en Pydantic Settings v2 con:
- Validación estricta de tipos
- Valores por defecto seguros
- Documentación inline
- Feature flags
- Environment-specific overrides
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _resolve_templates_dirs() -> List[str]:
    """Resolve template paths using api/templates as single source of truth."""
    # Use repo root as base
    project_root = Path(__file__).parent.parent.parent.parent.resolve()

    candidates = []
    if os.getenv("VERCEL"):
        candidates.append("/var/task/api/templates")
        candidates.append("/var/task/templates")
        candidates.append(str(project_root / "api" / "templates"))

    candidates.append(str(project_root / "api" / "templates"))
    candidates.append(str(Path.cwd() / "api" / "templates"))

    # Keep only existing directories plus serverless runtime paths on Vercel.
    is_vercel = bool(os.getenv("VERCEL"))
    valid_paths = []
    for p in candidates:
        if os.path.isdir(p) or (is_vercel and p.startswith("/var/task")):
            if p not in valid_paths:
                valid_paths.append(p)

    if not valid_paths:
        valid_paths = [str(project_root / "api" / "templates")]

    return valid_paths


def _resolve_static_dir() -> str:
    """Resolve static files directory."""
    project_root = Path(__file__).parent.parent.parent.parent.resolve()
    if os.getenv("VERCEL"):
        return str(Path.cwd() / "static")
    return str(project_root / "static")


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos."""

    class Config:
        env_prefix = "DB_"
        extra = "ignore"

    url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (Supabase)",
        alias="DATABASE_URL",
    )
    pool_size: int = Field(default=5, ge=1, le=20)
    max_overflow: int = Field(default=10, ge=0)
    pool_timeout: int = Field(default=30, ge=5)

    @property
    def is_configured(self) -> bool:
        return bool(self.url and "localhost" not in self.url.lower())

    @property
    def is_serverless(self) -> bool:
        """Detecta si estamos en entorno serverless (Vercel)."""
        return bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

    @validator("url")
    @classmethod
    def validate_serverless_port(cls, v: Optional[str]) -> Optional[str]:
        """Warn si se usa puerto 5432 en serverless (debe ser 6543)."""
        if v and ":5432" in v and os.getenv("VERCEL"):
            logger.warning(
                "🔥 CRITICAL: Using port 5432 (Session Mode) in Serverless. "
                "Switch to port 6543 (Transaction Pooler) to avoid connection limits."
            )
        return v


class RedisSettings(BaseSettings):
    """Configuración de Redis (Upstash)."""

    class Config:
        env_prefix = "UPSTASH_REDIS_"
        extra = "ignore"

    rest_url: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_URL")
    rest_token: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_TOKEN")
    url: Optional[str] = Field(default=None, alias="REDIS_URL")

    @property
    def is_configured(self) -> bool:
        return bool(self.url or (self.rest_url and self.rest_token))


class MetaSettings(BaseSettings):
    """Configuración de Meta (Facebook) Ads."""

    class Config:
        env_prefix = "META_"
        extra = "ignore"

    pixel_id: str = Field(default="")
    access_token: Optional[str] = Field(default=None)
    api_version: str = Field(default="v21.0")
    test_event_code: Optional[str] = Field(default=None)
    sandbox_mode: bool = Field(default=False)

    @property
    def is_configured(self) -> bool:
        return bool(self.pixel_id and self.access_token)

    @property
    def api_url(self) -> str:
        """URL completa para Meta CAPI."""
        return f"https://graph.facebook.com/{self.api_version}/{self.pixel_id}/events"


class SecuritySettings(BaseSettings):
    """Configuración de seguridad."""

    class Config:
        env_prefix = ""
        extra = "ignore"

    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    admin_key: str = Field(default="admin-change-me", alias="ADMIN_KEY")
    turnstile_site_key: str = Field(default="")
    turnstile_secret_key: Optional[str] = Field(default=None)

    # CORS
    cors_origins: List[str] = Field(
        default=[
            "https://jorgeaguirreflores.com",
            "https://www.jorgeaguirreflores.com",
            "http://localhost:8000",
        ],
        alias="CORS_ALLOWED_ORIGINS",
    )

    @validator("cors_origins", pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        """Parsea string de env var a lista."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


class FeatureFlags(BaseSettings):
    """
    Feature Flags - Control de funcionalidades sin deploy.

    Se pueden modificar via Vercel env vars sin código nuevo.
    """

    class Config:
        env_prefix = "FLAG_"
        extra = "ignore"

    show_testimonials: bool = Field(default=True)
    show_gallery: bool = Field(default=True)
    enable_chat_widget: bool = Field(default=False)
    enable_heatmap: bool = Field(default=False)
    meta_tracking: bool = Field(default=True)
    maintenance_mode: bool = Field(default=False)
    booking_enabled: bool = Field(default=True)

    # A/B Testing
    cta_variant: Literal["whatsapp", "form", "call"] = Field(default="whatsapp")
    hero_style: Literal["premium", "minimal", "video"] = Field(default="premium")


class ObservabilitySettings(BaseSettings):
    """Configuración de observabilidad."""

    class Config:
        env_prefix = ""
        extra = "ignore"

    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    clarity_project_id: Optional[str] = Field(default=None)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def sentry_enabled(self) -> bool:
        return bool(self.sentry_dsn)


class ExternalServicesSettings(BaseSettings):
    """Configuración de servicios externos."""

    class Config:
        extra = "ignore"

    # n8n

    # n8n
    n8n_webhook_url: Optional[str] = Field(default=None)

    # QStash
    qstash_token: Optional[str] = Field(default=None)
    qstash_url: Optional[str] = Field(default=None)

    # Google
    google_api_key: Optional[str] = Field(default=None)
    google_client_id: Optional[str] = Field(default=None)


class ServerSettings(BaseSettings):
    """Configuración del servidor."""

    class Config:
        env_prefix = ""
        extra = "ignore"

    host: str = Field(default="0.0.0.0", alias="HOST")  # nosec B104
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=1, ge=1, le=4)
    reload: bool = Field(default=False)

    @property
    def is_production(self) -> bool:
        return os.getenv("VERCEL") is not None or os.getenv("ENVIRONMENT") == "production"


class Settings(BaseSettings):
    """
    🎛️ Configuración centralizada de la aplicación.

    Todas las configuraciones se cargan desde:
    1. Variables de entorno (prioridad alta)
    2. Archivo .env (solo desarrollo local)
    3. Valores por defecto (prioridad baja)

    Usage:
        >>> from app.infrastructure.config import get_settings
        >>> settings = get_settings()
        >>> if settings.meta.is_configured:
        ...     print(f"Pixel ID: {settings.meta.pixel_id}")
    """

    class Config:
        env_file = ".env" if not os.getenv("VERCEL") else None
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

    # Sub-configuraciones organizadas por dominio
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    meta: MetaSettings = Field(default_factory=MetaSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    external: ExternalServicesSettings = Field(default_factory=ExternalServicesSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    # App metadata
    app_name: str = Field(default="Jorge Aguirre Flores Web")
    app_version: str = Field(default="3.0.0")
    debug: bool = Field(default=False)

    @property
    def system_version(self) -> str:
        """Alias for Neuro-Vision compatibility."""
        return self.app_version

    def resolve_tenant(self, tenant_id: Optional[str]) -> str:
        """Resolve tenant ID to a valid tenant string."""
        return tenant_id or "default"

    def is_tenant_allowed(self, tenant_id: str) -> bool:
        """Check if tenant is allowed to perform operations."""
        return True

    @property
    def whatsapp_url(self) -> str:
        """URL de WhatsApp con número configurado."""
        return "https://wa.me/59164714751"

    @property
    def templates_dir(self) -> str:
        """Single source of truth for templates."""
        dirs = _resolve_templates_dirs()
        return dirs[0] if dirs else ""

    @property
    def static_dir(self) -> str:
        """Single source of truth for static files."""
        return _resolve_static_dir()

    # =================================================================
    # 🏛️ Legacy Compatibility Aliases (Flat access)
    # =================================================================
    @property
    def DATABASE_URL(self) -> Optional[str]:
        return self.db.url

    @DATABASE_URL.setter
    def DATABASE_URL(self, value: Optional[str]):
        self.db.url = value

    @property
    def UPSTASH_REDIS_REST_URL(self) -> Optional[str]:
        return self.redis.rest_url

    @UPSTASH_REDIS_REST_URL.setter
    def UPSTASH_REDIS_REST_URL(self, value: Optional[str]):
        self.redis.rest_url = value

    @property
    def UPSTASH_REDIS_REST_TOKEN(self) -> Optional[str]:
        return self.redis.rest_token

    @property
    def META_PIXEL_ID(self) -> str:
        return self.meta.pixel_id

    @META_PIXEL_ID.setter
    def META_PIXEL_ID(self, value: str):
        self.meta.pixel_id = value

    @property
    def META_ACCESS_TOKEN(self) -> Optional[str]:
        return self.meta.access_token

    @META_ACCESS_TOKEN.setter
    def META_ACCESS_TOKEN(self, value: Optional[str]):
        self.meta.access_token = value

    @property
    def TEST_EVENT_CODE(self) -> Optional[str]:
        return self.meta.test_event_code

    @property
    def META_SANDBOX_MODE(self) -> bool:
        return self.meta.sandbox_mode

    @property
    def meta_api_url(self) -> str:
        return self.meta.api_url

    @property
    def ADMIN_KEY(self) -> str:
        return self.security.admin_key

    @ADMIN_KEY.setter
    def ADMIN_KEY(self, value: str):
        self.security.admin_key = value

    @property
    def TURNSTILE_SECRET_KEY(self) -> Optional[str]:
        return self.security.turnstile_secret_key

    @TURNSTILE_SECRET_KEY.setter
    def TURNSTILE_SECRET_KEY(self, value: Optional[str]):
        self.security.turnstile_secret_key = value

    @property
    def FLAG_HERO_STYLE(self) -> str:
        return self.features.hero_style

    @property
    def FLAG_META_TRACKING(self) -> bool:
        return self.features.meta_tracking

    @property
    def FLAG_MAINTENANCE_MODE(self) -> bool:
        return self.features.maintenance_mode

    @property
    def FLAG_BOOKING_ENABLED(self) -> bool:
        return self.features.booking_enabled

    @property
    def FLAG_SHOW_TESTIMONIALS(self) -> bool:
        return self.features.show_testimonials

    @property
    def QSTASH_TOKEN(self) -> Optional[str]:
        return self.external.qstash_token

    @property
    def N8N_WEBHOOK_URL(self) -> Optional[str]:
        return self.external.n8n_webhook_url

    @property
    def GROQ_API_KEY(self) -> Optional[str]:
        return self.external.google_api_key

    @property
    def vercel_url(self) -> Optional[str]:
        """Vercel environment URL."""
        return os.getenv("VERCEL_URL")

    @property
    def FLAG_SHOW_GALLERY(self) -> bool:
        return self.features.show_gallery

    @property
    def FLAG_ENABLE_CHAT_WIDGET(self) -> bool:
        return self.features.enable_chat_widget

    @property
    def FLAG_CTA_VARIANT(self) -> str:
        return self.features.cta_variant

    @property
    def FLAG_ENABLE_HEATMAP(self) -> bool:
        return self.features.enable_heatmap

    @property
    def TURNSTILE_SITE_KEY(self) -> str:
        return self.security.turnstile_site_key

    @property
    def TEMPLATES_DIR(self) -> str:
        return self.templates_dir

    @property
    def TEMPLATES_DIRS(self) -> list[str]:
        return [self.templates_dir]

    @property
    def CLARITY_PROJECT_ID(self) -> Optional[str]:
        return self.observability.clarity_project_id

    @property
    def GOOGLE_CLIENT_ID(self) -> Optional[str]:
        return self.external.google_client_id

    @property
    def BASE_DIR(self) -> str:
        return str(Path(__file__).parent.parent.parent.parent.resolve())

    @property
    def redis_enabled(self) -> bool:
        return self.redis.is_configured

    @property
    def SENTRY_DSN(self) -> Optional[str]:
        return self.observability.sentry_dsn

    @property
    def STATIC_DIR(self) -> str:
        return self.static_dir

    @property
    def HOST(self) -> str:
        return self.server.host

    @property
    def WHATSAPP_NUMBER(self) -> str:
        return "59164714751"

    @property
    def CELERY_BROKER_URL(self) -> Optional[str]:
        """Legacy Celery broker URL (not actively used in serverless)."""
        return self.redis.url or self.redis.rest_url

    @property
    def CORS_ALLOWED_ORIGINS(self) -> List[str]:
        return self.security.cors_origins

    # =================================================================

    def validate_critical(self) -> list[str]:
        """
        Valida configuración crítica y retorna warnings.

        Returns:
            Lista de mensajes de warning (vacía si todo OK).
        """
        warnings: list[str] = []

        if not self.meta.pixel_id:
            warnings.append("META_PIXEL_ID no configurado")

        if not self.meta.access_token:
            warnings.append("META_ACCESS_TOKEN no configurado")

        if not self.db.url:
            warnings.append("DATABASE_URL no configurado - usando SQLite fallback")

        if not self.redis.is_configured:
            warnings.append("Redis no configurado - usando in-memory cache")

        return warnings

    def log_status(self) -> None:
        """Loguea el estado de la configuración al startup."""
        logger.info(f"🚀 {self.app_name} v{self.app_version}")
        logger.info(f"📊 Meta Pixel: {'✅' if self.meta.is_configured else '❌'}")
        logger.info(f"🗄️  Database: {'✅' if self.db.is_configured else '⚠️ SQLite'}")
        logger.info(f"⚡ Redis: {'✅' if self.redis.is_configured else '⚠️ Memory'}")
        logger.info(f"🛡️ Sentry: {'✅' if self.observability.sentry_enabled else '❌'}")

        for warning in self.validate_critical():
            logger.warning(f"⚠️ {warning}")


@lru_cache()
def get_settings() -> Settings:
    """
    Factory para Settings singleton.

    Usa LRU cache para evitar recargar configuración.
    """
    return Settings()


# Export singleton para conveniencia
settings = get_settings()
