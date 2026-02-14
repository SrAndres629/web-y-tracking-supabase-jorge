"""
💉 API Dependencies.

Factories para inyección de dependencias en FastAPI.

Estas funciones son usadas con Depends() para proveer
instancias de handlers y servicios a los routes.
"""

from __future__ import annotations

import hashlib
import logging
import time
from functools import lru_cache
from typing import List, Optional, Any, Dict, Tuple

from fastapi import Depends, Header, HTTPException, Request
from app.application.commands.track_event import TrackEventHandler
from app.application.commands.create_visitor import CreateVisitorHandler
from app.application.queries.get_content import GetContentHandler
from app.application.interfaces.cache_port import DeduplicationPort, ContentCachePort
from app.application.interfaces.tracker_port import TrackerPort
from app.domain.repositories.visitor_repo import VisitorRepository
from app.domain.repositories.event_repo import EventRepository
from app.domain.repositories.lead_repo import LeadRepository
from app.config import settings

logger = logging.getLogger(__name__)


# ===== Cache =====

@lru_cache()
def get_deduplicator() -> DeduplicationPort:
    """Provee deduplicador (Redis o memoria)."""
    from app.infrastructure.config import get_settings
    from app.infrastructure.cache import RedisDeduplication, InMemoryDeduplication
    
    settings = get_settings()
    if settings.redis.is_configured:
        return RedisDeduplication()
    return InMemoryDeduplication()


@lru_cache()
def get_content_cache() -> ContentCachePort:
    """Provee cache de contenido."""
    from app.infrastructure.config import get_settings
    from app.infrastructure.cache import RedisContentCache, InMemoryContentCache
    
    settings = get_settings()
    if settings.redis.is_configured:
    return RedisContentCache()
    return InMemoryContentCache()


# ===== Repositories =====

@lru_cache()
def get_visitor_repository() -> VisitorRepository:
    """Provee repositorio de visitantes."""
    from app.infrastructure.persistence.visitor_repo import PostgreSQLVisitorRepository
    return PostgreSQLVisitorRepository()


def get_event_repository() -> EventRepository:
    """Provee repositorio de eventos."""
    from app.infrastructure.persistence.event_repo import PostgreSQLEventRepository
    return PostgreSQLEventRepository()


@lru_cache()
def get_lead_repository() -> LeadRepository:
    """Provee repositorio de leads."""
    from app.infrastructure.persistence.sql_lead_repo import SQLLeadRepository
    return SQLLeadRepository()


# ===== Trackers =====

_tracker_cache: Optional[List[TrackerPort]] = None

def get_trackers() -> List[TrackerPort]:
    """Provee lista de trackers configurados (singleton instances)."""
    global _tracker_cache
    if _tracker_cache is not None:
        return _tracker_cache
    
    from app.infrastructure.external.meta_capi import MetaTracker
    from app.infrastructure.external.rudderstack import RudderStackTracker
    
    _tracker_cache = [
        MetaTracker(),
        RudderStackTracker(),
    ]
    return _tracker_cache


# ===== Handlers =====

def get_track_event_handler(tenant_id: Optional[str] = Header(None, alias="x-tenant-id")) -> TrackEventHandler:
    """Provee handler para tracking de eventos."""
    resolved = settings.resolve_tenant(tenant_id)
    if not settings.is_tenant_allowed(resolved):
        raise HTTPException(status_code=403, detail="Tenant no permitido")
    handler = TrackEventHandler(
        deduplicator=get_deduplicator(),
        visitor_repo=get_visitor_repository(),
        event_repo=get_event_repository(),
        trackers=get_trackers(),
    )
    handler.tenant_id = resolved  # type: ignore[attr-defined]
    return handler


def get_create_visitor_handler() -> CreateVisitorHandler:
    """Provee handler para crear visitantes."""
    return CreateVisitorHandler(
        visitor_repo=get_visitor_repository(),
    )


def get_get_content_handler() -> GetContentHandler:
    """Provee handler para obtener contenido."""
    return GetContentHandler(
        cache=get_content_cache(),
    )


# ===== Legacy Compatibility Facade =====

class LegacyFacade:
    """
    Transitional facade that centralizes access to legacy modules.
    Keeps legacy dependencies out of route modules while migration continues.
    """

    def __init__(self) -> None:
        from app import database as database_module
        from app import meta_capi as meta_capi_module
        from app.infrastructure.config import get_settings

        self._database = database_module
        self._meta_capi = meta_capi_module
        self._settings = get_settings()
        self._visitor_cache: Dict[str, Dict[str, Any]] = {}

    # Database helpers
    def check_connection(self) -> bool:
        return self._database.check_connection()

    def save_visitor(self, *args: Any, **kwargs: Any) -> None:
        self._database.save_visitor(*args, **kwargs)

    def get_or_create_lead(self, *args: Any, **kwargs: Any):
        return self._database.get_or_create_lead(*args, **kwargs)

    def upsert_contact_advanced(self, *args: Any, **kwargs: Any) -> None:
        self._database.upsert_contact_advanced(*args, **kwargs)

    def log_interaction(self, *args: Any, **kwargs: Any) -> bool:
        return self._database.log_interaction(*args, **kwargs)

    def get_visitor_by_id(self, visitor_id: int):
        return self._database.get_visitor_by_id(visitor_id)

    def get_all_visitors(self, limit: int = 50):
        return self._database.get_all_visitors(limit=limit)

    def get_cursor(self):
        return self._database.get_cursor()

    # Tracking helpers
    def generate_external_id(self, client_ip: str, user_agent: str) -> str:
        combined = f"{client_ip}_{user_agent}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]

    def send_n8n_webhook(self, payload: Dict[str, Any]) -> bool:
        webhook_url = self._settings.external.n8n_webhook_url
        if not webhook_url:
            return False
        try:
            import httpx

            response = httpx.post(webhook_url, json=payload, timeout=10.0)
            return response.status_code == 200
        except Exception as exc:
            logger.warning(f"n8n webhook send failed: {exc}")
            return False

    # Cache helpers
    def cache_visitor_data(self, external_id: str, data: Dict[str, Any]) -> None:
        self._visitor_cache[external_id] = {
            "data": data,
            "expires": time.time() + 24 * 3600,
        }

    def get_cached_visitor(self, external_id: str):
        item = self._visitor_cache.get(external_id)
        if not item:
            return None
        if item["expires"] < time.time():
            self._visitor_cache.pop(external_id, None)
            return None
        return item["data"]

    def redis_health_check(self):
        if not self._settings.redis.is_configured:
            return {"status": "disabled"}
        try:
            from upstash_redis import Redis

            client = Redis(
                url=self._settings.redis.rest_url,
                token=self._settings.redis.rest_token,
            )
            client.ping()
            return {"status": "ok"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    # Meta CAPI helper
    async def send_elite_event(self, **kwargs: Any):
        return await self._meta_capi.send_elite_event(**kwargs)


@lru_cache()
def get_legacy_facade() -> LegacyFacade:
    """Provide singleton legacy facade during migration period."""
    return LegacyFacade()
