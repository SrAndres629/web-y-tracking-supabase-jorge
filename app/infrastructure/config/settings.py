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

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Manual load to guarantee availability for Pydantic v2
load_dotenv(str(Path(__file__).parent.parent.parent.parent / ".env"))


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


class DatabaseSettings(BaseModel):
    """Configuración de base de datos."""
    model_config = SettingsConfigDict(extra="ignore")

    url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (Supabase)",
        alias="DATABASE_URL",
        validation_alias="DATABASE_URL",
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


class RedisSettings(BaseModel):
    """Configuración de Redis (Upstash)."""
    model_config = SettingsConfigDict(extra="ignore")

    rest_url: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_URL", validation_alias="UPSTASH_REDIS_REST_URL")
    rest_token: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_TOKEN", validation_alias="UPSTASH_REDIS_REST_TOKEN")
    url: Optional[str] = Field(default=None, alias="REDIS_URL", validation_alias="REDIS_URL")

    @property
    def is_configured(self) -> bool:
        return bool(self.url or (self.rest_url and self.rest_token))


class CloudflareSettings(BaseModel):
    """Configuración de Cloudflare / Zaraz."""
    model_config = SettingsConfigDict(extra="ignore")

    account_id: Optional[str] = Field(
        default=None,
        alias="CLOUDFLARE_ACCOUNT_ID",
        validation_alias="CLOUDFLARE_ACCOUNT_ID",
    )
    zone_id: Optional[str] = Field(
        default=None,
        alias="CLOUDFLARE_ZONE_ID",
        validation_alias="CLOUDFLARE_ZONE_ID",
    )
    api_token: Optional[str] = Field(
        default=None,
        alias="CLOUDFLARE_API_TOKEN",
        validation_alias="CLOUDFLARE_API_TOKEN",
    )
    zaraz_enabled: bool = Field(
        default=True,
        alias="ZARAZ_ENABLED",
        validation_alias="ZARAZ_ENABLED",
    )

    @property
    def is_configured(self) -> bool:
        return bool(self.account_id and self.zone_id)

    @property
    def can_manage_zone(self) -> bool:
        return bool(self.is_configured and self.api_token)


class MetaSettings(BaseModel):
    """Configuración de Meta (Facebook) Ads."""

    class Config:
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
    n8n_webhook_url: Optional[str] = Field(default=None)


    # QStash
    qstash_token: Optional[str] = Field(default=None)
    qstash_url: Optional[str] = Field(default=None)
    qstash_current_signing_key: Optional[str] = Field(default=None)
    qstash_next_signing_key: Optional[str] = Field(default=None)

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
    """
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / ".env") if not os.getenv("VERCEL") else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    # Sub-configuraciones organizadas por dominio
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    cloudflare: CloudflareSettings = Field(default_factory=CloudflareSettings)
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

    # Core Env Vars (Flattened for reliability)
    DATABASE_URL: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")
    UPSTASH_REDIS_REST_URL: Optional[str] = Field(default=None, validation_alias="UPSTASH_REDIS_REST_URL")
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = Field(default=None, validation_alias="UPSTASH_REDIS_REST_TOKEN")
    REDIS_URL: Optional[str] = Field(default=None, validation_alias="REDIS_URL")
    META_PIXEL_ID: str = Field(default="", validation_alias="META_PIXEL_ID")
    META_ACCESS_TOKEN: Optional[str] = Field(default=None, validation_alias="META_ACCESS_TOKEN")
    META_API_VERSION: str = Field(default="v21.0", validation_alias="META_API_VERSION")
    META_SANDBOX_MODE: bool = Field(default=False, validation_alias="META_SANDBOX_MODE")
    QSTASH_TOKEN: Optional[str] = Field(default=None, validation_alias="QSTASH_TOKEN")
    QSTASH_CURRENT_SIGNING_KEY: Optional[str] = Field(default=None, validation_alias="QSTASH_CURRENT_SIGNING_KEY")
    QSTASH_NEXT_SIGNING_KEY: Optional[str] = Field(default=None, validation_alias="QSTASH_NEXT_SIGNING_KEY")
    TEST_EVENT_CODE: Optional[str] = Field(default=None, validation_alias="TEST_EVENT_CODE")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = Field(default=None, validation_alias="CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_ZONE_ID: Optional[str] = Field(default=None, validation_alias="CLOUDFLARE_ZONE_ID")
    CLOUDFLARE_API_TOKEN: Optional[str] = Field(default=None, validation_alias="CLOUDFLARE_API_TOKEN")
    ZARAZ_ENABLED: bool = Field(default=True, validation_alias="ZARAZ_ENABLED")
    CONFIG_STRICT_STARTUP: bool = Field(default=False, validation_alias="CONFIG_STRICT_STARTUP")

    @property
    def system_version(self) -> str:
        return self.app_version

    def resolve_tenant(self, tenant_id: Optional[str]) -> str:
        return tenant_id or "default"

    def is_tenant_allowed(self, tenant_id: str) -> bool:
        return True

    @property
    def whatsapp_url(self) -> str:
        return "https://wa.me/59164714751"

    @property
    def templates_dir(self) -> str:
        dirs = _resolve_templates_dirs()
        return dirs[0] if dirs else ""

    @property
    def static_dir(self) -> str:
        return _resolve_static_dir()

    @model_validator(mode="after")
    def sync_nested_settings(self) -> Settings:
        """Sync flattened env vars to nested models for backward compatibility."""
        if self.DATABASE_URL:
            self.db.url = self.DATABASE_URL
        if self.UPSTASH_REDIS_REST_URL:
            self.redis.rest_url = self.UPSTASH_REDIS_REST_URL
        if self.UPSTASH_REDIS_REST_TOKEN:
            self.redis.rest_token = self.UPSTASH_REDIS_REST_TOKEN
        if self.REDIS_URL:
            self.redis.url = self.REDIS_URL
        if self.CLOUDFLARE_ACCOUNT_ID:
            self.cloudflare.account_id = self.CLOUDFLARE_ACCOUNT_ID
        if self.CLOUDFLARE_ZONE_ID:
            self.cloudflare.zone_id = self.CLOUDFLARE_ZONE_ID
        if self.CLOUDFLARE_API_TOKEN:
            self.cloudflare.api_token = self.CLOUDFLARE_API_TOKEN
        self.cloudflare.zaraz_enabled = bool(self.ZARAZ_ENABLED)
        if self.META_PIXEL_ID:
            self.meta.pixel_id = self.META_PIXEL_ID
        if self.META_ACCESS_TOKEN:
            self.meta.access_token = self.META_ACCESS_TOKEN
        if self.META_API_VERSION:
            self.meta.api_version = self.META_API_VERSION
        if self.META_SANDBOX_MODE is not None:
            self.meta.sandbox_mode = self.META_SANDBOX_MODE
        if self.QSTASH_TOKEN:
            self.external.qstash_token = self.QSTASH_TOKEN
        if self.QSTASH_CURRENT_SIGNING_KEY:
            self.external.qstash_current_signing_key = self.QSTASH_CURRENT_SIGNING_KEY
        if self.QSTASH_NEXT_SIGNING_KEY:
            self.external.qstash_next_signing_key = self.QSTASH_NEXT_SIGNING_KEY
        if self.GOOGLE_API_KEY:
            self.external.google_api_key = self.GOOGLE_API_KEY
        return self

    # =================================================================
    # 🏛️ Legacy Compatibility Aliases (Flat access)
    # =================================================================
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
    def CORS_ALLOWED_ORIGINS(self) -> List[str]:
        return self.security.cors_origins

    # =================================================================
    # 🔒 Integration Contract
    # =================================================================

    def integration_contract(self) -> dict[str, dict[str, str | bool]]:
        """Estado de integraciones críticas para operación y observabilidad."""
        return {
            "supabase_db": {
                "configured": self.db.is_configured,
                "mode": "postgres" if self.db.is_configured else "fallback",
            },
            "redis_upstash": {
                "configured": self.redis.is_configured,
                "mode": "redis" if self.redis.is_configured else "memory",
            },
            "qstash": {
                "configured": bool(self.external.qstash_token),
                "mode": "enabled" if self.external.qstash_token else "disabled",
            },
            "cloudflare_core": {
                "configured": self.cloudflare.is_configured,
                "mode": "managed" if self.cloudflare.is_configured else "unmanaged",
            },
            "cloudflare_api": {
                "configured": self.cloudflare.can_manage_zone,
                "mode": "rw" if self.cloudflare.can_manage_zone else "readonly",
            },
            "zaraz": {
                "configured": self.cloudflare.zaraz_enabled,
                "mode": "realtime_expected" if self.cloudflare.zaraz_enabled else "disabled",
            },
        }

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
        if not self.cloudflare.is_configured:
            warnings.append("Cloudflare no configurado completamente (zone/account)")
        if not self.cloudflare.can_manage_zone:
            warnings.append("Cloudflare API token ausente - purge/zaraz API deshabilitado")
        if not self.cloudflare.zaraz_enabled:
            warnings.append("Zaraz deshabilitado por configuración")

        return warnings

    def enforce_contract(self) -> None:
        """
        En modo estricto, aborta boot si faltan integraciones core.
        """
        if not self.CONFIG_STRICT_STARTUP:
            return

        missing: list[str] = []
        if not self.db.is_configured:
            missing.append("supabase_db")
        if not self.redis.is_configured:
            missing.append("redis_upstash")
        if not self.cloudflare.is_configured:
            missing.append("cloudflare_core")
        if not self.cloudflare.zaraz_enabled:
            missing.append("zaraz")

        if missing:
            raise RuntimeError(
                "CONFIG_STRICT_STARTUP=1 but integration contract is incomplete: "
                + ", ".join(missing)
            )

    def log_status(self) -> None:
        """Loguea el estado de la configuración al startup."""
        logger.info(f"🚀 {self.app_name} v{self.app_version}")
        logger.info(f"📊 Meta Pixel: {'✅' if self.meta.is_configured else '❌'}")
        logger.info(f"🗄️  Database: {'✅' if self.db.is_configured else '⚠️ SQLite'}")
        logger.info(f"⚡ Redis: {'✅' if self.redis.is_configured else '⚠️ Memory'}")
        logger.info(f"☁️ Cloudflare: {'✅' if self.cloudflare.is_configured else '⚠️ Partial'}")
        logger.info(f"🧩 Zaraz: {'✅' if self.cloudflare.zaraz_enabled else '❌'}")
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
