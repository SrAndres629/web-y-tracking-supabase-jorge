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
from typing import Any, Dict, List, Optional

from fastapi import Header, HTTPException

from app.application.commands.create_lead import CreateLeadHandler
from app.application.commands.create_visitor import CreateVisitorHandler
from app.application.commands.track_event import TrackEventHandler
from app.application.interfaces.cache_port import DeduplicationPort
from app.application.interfaces.tracker_port import TrackerPort
from app.domain.repositories.event_repo import EventRepository
from app.domain.repositories.lead_repo import LeadRepository
from app.domain.repositories.visitor_repo import VisitorRepository
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


# ===== Cache =====


@lru_cache()
def get_deduplicator() -> DeduplicationPort:
    """Provee deduplicador (Redis o memoria)."""
    from app.infrastructure.cache import InMemoryDeduplication, RedisDeduplication
    from app.infrastructure.config import get_settings

    settings = get_settings()
    if settings.redis.is_configured:
        return RedisDeduplication()
    return InMemoryDeduplication()


# ===== Repositories =====


@lru_cache()
def get_visitor_repository() -> VisitorRepository:
    """Provee repositorio de visitantes."""
    from app.infrastructure.persistence.repositories.visitor_repository import (
        VisitorRepository as NativeVisitorRepo,
    )

    return NativeVisitorRepo()


@lru_cache()
def get_event_repository() -> EventRepository:
    """Provee repositorio de eventos."""
    from app.infrastructure.persistence.repositories.event_repository import (
        PostgreSQLEventRepository,
    )

    return PostgreSQLEventRepository()


@lru_cache()
def get_lead_repository() -> LeadRepository:
    """Provee repositorio de leads."""
    from app.infrastructure.persistence.repositories.lead_repository import (
        LeadRepository as NativeLeadRepo,
    )

    return NativeLeadRepo()


# ===== Trackers =====

_tracker_cache: Optional[List[TrackerPort]] = None


def get_trackers() -> List[TrackerPort]:
    """Provee lista de trackers configurados (singleton instances)."""
    global _tracker_cache
    if _tracker_cache is not None:
        return _tracker_cache

    from app.tracking import MetaTracker, TinybirdTracker

    _tracker_cache = [
        MetaTracker(),
        TinybirdTracker(),
    ]
    return _tracker_cache


# ===== Handlers =====


def get_track_event_handler(
    tenant_id: Optional[str] = Header(None, alias="x-tenant-id"),
) -> TrackEventHandler:
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


def get_create_lead_handler() -> CreateLeadHandler:
    """Provee handler para crear leads."""
    return CreateLeadHandler(
        lead_repo=get_lead_repository(),
        visitor_repo=get_visitor_repository(),
    )


def get_create_visitor_handler() -> CreateVisitorHandler:
    """Provee handler para crear visitantes."""
    return CreateVisitorHandler(
        visitor_repo=get_visitor_repository(),
    )


# Handlers and other factories remain as is.


class _LegacyFacade:
    """
    Backwards-compatible facade providing legacy API for routes.

    All routes reference `legacy.*` methods. This facade delegates
    to the actual implementations in tracking.py / meta_capi.py.
    """

    # ── Health Check ──────────────────────────────────────────────
    @staticmethod
    def check_connection() -> bool:
        try:
            from app.database import check_connection
            return check_connection()
        except Exception:
            return False

    # ── Identity ──────────────────────────────────────────────────
    @staticmethod
    def generate_external_id(ip: str, user_agent: str) -> str:
        from app.core.validators import generate_external_id
        return generate_external_id(ip, user_agent)

    # ── Visitor Persistence ───────────────────────────────────────
    @staticmethod
    def save_visitor(
        external_id: str,
        fbclid: str,
        client_ip: str,
        user_agent: str,
        source: str,
        utm_data=None,
        email=None,
        phone=None,
    ) -> None:
        """Persists visitor data — delegates to cache + DB (best-effort)."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            from app.tracking import cache_visitor_data
            data = {
                "fbclid": fbclid,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "source": source,
                "utm_data": utm_data or {},
            }
            if email:
                data["email"] = email
            if phone:
                data["phone"] = phone
            cache_visitor_data(external_id, data)
        except Exception as e:
            logger.warning("⚠️ save_visitor fallback: %s", e)

    # ── Meta CAPI (Elite Event Sender) ────────────────────────────
    @staticmethod
    async def send_elite_event(**kwargs):
        """Delegates to tracking.send_elite_event."""
        from app.tracking import send_elite_event
        return await send_elite_event(**kwargs)

    # ── Webhook ───────────────────────────────────────────────────
    @staticmethod
    def send_n8n_webhook(event_data) -> bool:
        """Delegates to tracking.send_n8n_webhook."""
        from app.tracking import send_n8n_webhook
        return send_n8n_webhook(event_data)

    # ── CRM Contact Sync ─────────────────────────────────────────
    @staticmethod
    def upsert_contact_advanced(payload) -> None:
        """CRM contact sync — safe no-op (legacy function removed in DDD refactor)."""
        import logging
        logging.getLogger(__name__).debug("upsert_contact_advanced: no-op (DDD)")

    # ── Visitor Cache ─────────────────────────────────────────────
    @staticmethod
    def get_cached_visitor(external_id: str):
        """Retrieves cached visitor data."""
        from app.tracking import get_cached_visitor
        return get_cached_visitor(external_id)

    @staticmethod
    def cache_visitor_data(external_id: str, data, ttl_hours: int = 24) -> None:
        """Caches visitor data in Redis."""
        from app.tracking import cache_visitor_data
        cache_visitor_data(external_id, data, ttl_hours)


def get_legacy_facade() -> _LegacyFacade:
    """Provee facade legacy para health checks y routes."""
    return _LegacyFacade()
