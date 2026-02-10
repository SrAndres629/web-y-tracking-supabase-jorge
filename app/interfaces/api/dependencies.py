"""
💉 API Dependencies.

Factories para inyección de dependencias en FastAPI.

Estas funciones son usadas con Depends() para proveer
instancias de handlers y servicios a los routes.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from app.application.commands.track_event import TrackEventHandler
from app.application.commands.create_visitor import CreateVisitorHandler
from app.application.queries.get_content import GetContentHandler
from app.application.interfaces.cache_port import DeduplicationPort, ContentCachePort
from app.application.interfaces.tracker_port import TrackerPort
from app.domain.repositories.visitor_repo import VisitorRepository
from app.domain.repositories.event_repo import EventRepository
from app.domain.repositories.lead_repo import LeadRepository


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
    # TODO: Implementar
    from app.infrastructure.persistence.event_repo import PostgreSQLEventRepository
    return PostgreSQLEventRepository()


def get_lead_repository() -> LeadRepository:
    """Provee repositorio de leads."""
    # TODO: Implementar
    raise NotImplementedError("Lead repository not yet implemented")


# ===== Trackers =====

def get_trackers() -> List[TrackerPort]:
    """Provee lista de trackers configurados."""
    from app.infrastructure.external.meta_capi import MetaTracker
    from app.infrastructure.external.rudderstack import RudderStackTracker
    
    trackers: List[TrackerPort] = []
    
    # Meta CAPI
    trackers.append(MetaTracker())
    
    # RudderStack
    trackers.append(RudderStackTracker())
    
    return trackers


# ===== Handlers =====

def get_track_event_handler() -> TrackEventHandler:
    """Provee handler para tracking de eventos."""
    return TrackEventHandler(
        deduplicator=get_deduplicator(),
        visitor_repo=get_visitor_repository(),
        event_repo=get_event_repository(),
        trackers=get_trackers(),
    )


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
