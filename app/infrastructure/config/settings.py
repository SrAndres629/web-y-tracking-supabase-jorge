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

import os
import logging
from typing import Optional, List, Literal
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos."""
    
    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")
    
    url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (Supabase)",
        alias="DATABASE_URL"
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
    
    @field_validator("url")
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
    
    model_config = SettingsConfigDict(env_prefix="UPSTASH_REDIS_", extra="ignore")
    
    rest_url: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_URL")
    rest_token: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_TOKEN")
    
    @property
    def is_configured(self) -> bool:
        return bool(self.rest_url and self.rest_token)


class MetaSettings(BaseSettings):
    """Configuración de Meta (Facebook) Ads."""
    
    model_config = SettingsConfigDict(env_prefix="META_", extra="ignore")
    
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
    
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    
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
        alias="CORS_ALLOWED_ORIGINS"
    )
    
    @field_validator("cors_origins", mode="before")
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
    
    model_config = SettingsConfigDict(env_prefix="FLAG_", extra="ignore")
    
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
    
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    clarity_project_id: Optional[str] = Field(default=None)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    @property
    def sentry_enabled(self) -> bool:
        return bool(self.sentry_dsn)


class ExternalServicesSettings(BaseSettings):
    """Configuración de servicios externos."""
    
    model_config = SettingsConfigDict(extra="ignore")
    
    # RudderStack
    rudderstack_write_key: Optional[str] = Field(default=None)
    rudderstack_data_plane_url: Optional[str] = Field(default=None)
    
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
    
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    
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
    
    model_config = SettingsConfigDict(
        env_file=".env" if not os.getenv("VERCEL") else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
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
    def whatsapp_url(self) -> str:
        """URL de WhatsApp con número configurado."""
        return "https://wa.me/59164714751"
    
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
