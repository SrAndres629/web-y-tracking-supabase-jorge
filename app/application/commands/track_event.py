"""
📊 Track Event Command.

Caso de uso: Registrar un evento de tracking.
Orquesta deduplicación, persistencia y envío a trackers externos.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from app.core.result import Result, Err
from app.domain.models.events import TrackingEvent, EventName
from app.domain.models.values import ExternalId, UTMParams
from app.domain.repositories.visitor_repo import VisitorRepository
from app.domain.repositories.event_repo import EventRepository
from app.application.dto.tracking_dto import (
    TrackEventRequest,
    TrackEventResponse,
    TrackingContext,
)
from app.application.interfaces.tracker_port import TrackerPort
from app.application.interfaces.cache_port import DeduplicationPort

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrackEventCommand:
    """Input para el handler."""
    request: TrackEventRequest
    context: TrackingContext


class TrackEventHandler:
    """
    Handler para trackear eventos.
    
    Flujo:
    1. Deduplicación (cache rápido)
    2. Obtener/crear visitante
    3. Crear evento de dominio
    4. Persistir evento
    5. Enviar a trackers externos (async)
    
    Es idempotente: mismo event_id = mismo resultado.
    """
    
    def __init__(
        self,
        deduplicator: DeduplicationPort,
        visitor_repo: VisitorRepository,
        event_repo: EventRepository,
        trackers: List[TrackerPort],
    ):
        self.deduplicator = deduplicator
        self.visitor_repo = visitor_repo
        self.event_repo = event_repo
        self.trackers = trackers
    
    async def handle(self, cmd: TrackEventCommand) -> TrackEventResponse:
        """
        Ejecuta el caso de uso.
        
        Args:
            cmd: Comando con request y contexto
            
        Returns:
            TrackEventResponse con resultado
        """
        try:
            # 1. Parsear EventName
            try:
                event_name = EventName(cmd.request.event_name)
            except ValueError:
                return TrackEventResponse.error(f"Invalid event name: {cmd.request.event_name}")
            
            # 2. Crear ExternalId
            external_id_result = ExternalId.from_string(cmd.request.external_id)
            if external_id_result.is_err:
                return TrackEventResponse.error(external_id_result.unwrap_err())
            external_id = external_id_result.unwrap()
            
            # 3. Verificar deduplicación (fast path)
            event_id_str = f"{cmd.request.event_name}:{external_id.value}:{int(datetime.utcnow().timestamp() / 3600)}"
            if not await self.deduplicator.is_unique(event_id_str):
                logger.info(f"🔄 Duplicate event blocked: {event_id_str}")
                return TrackEventResponse.duplicate(event_id_str)
            
            # 4. Obtener o crear visitante
            visitor = await self.visitor_repo.get_by_external_id(external_id)
            if not visitor:
                # Crear visitante implícitamente
                from app.domain.models.visitor import Visitor, VisitorSource
                visitor = Visitor.create(
                    ip=cmd.context.ip_address,
                    user_agent=cmd.context.user_agent,
                    fbclid=cmd.request.fbclid,
                    fbp=cmd.request.fbp,
                    source=VisitorSource.PAGEVIEW,
                    utm=UTMParams.from_dict({
                        "utm_source": cmd.request.utm_source,
                        "utm_medium": cmd.request.utm_medium,
                        "utm_campaign": cmd.request.utm_campaign,
                        "utm_term": cmd.request.utm_term,
                        "utm_content": cmd.request.utm_content,
                    }),
                )
                await self.visitor_repo.save(visitor)
            else:
                # Actualizar visitante existente
                visitor.record_visit()
                if cmd.request.fbclid:
                    visitor.update_fbclid(cmd.request.fbclid)
                if cmd.request.fbp:
                    visitor.update_fbp(cmd.request.fbp)
                await self.visitor_repo.update(visitor)
            
            # 5. Crear evento de dominio
            event = TrackingEvent.create(
                event_name=event_name,
                external_id=external_id,
                source_url=cmd.request.source_url,
                custom_data=cmd.request.custom_data,
                utm=UTMParams.from_dict({
                    "utm_source": cmd.request.utm_source,
                    "utm_medium": cmd.request.utm_medium,
                    "utm_campaign": cmd.request.utm_campaign,
                }),
            )
            
            # 6. Persistir evento
            await self.event_repo.save(event)
            
            # 7. Enviar a trackers externos (fire and forget)
            import asyncio
            asyncio.create_task(self._send_to_trackers(event, visitor))
            
            logger.info(f"✅ Event tracked: {event.event_name.value} ({event.event_id})")
            return TrackEventResponse(
                success=True,
                event_id=event.event_id.value,
                status="queued",
                message=f"{event.event_name.value} tracked successfully"
            )
            
        except Exception as e:
            logger.exception(f"❌ Error tracking event: {e}")
            return TrackEventResponse.error(str(e))
    
    async def _send_to_trackers(self, event: TrackingEvent, visitor) -> None:
        """
        Envia evento a todos los trackers configurados.
        
        No lanza excepciones - errores se loguean silenciosamente.
        """
        if not self.trackers:
            return
        
        tasks = []
        for tracker in self.trackers:
            try:
                task = tracker.track(event, visitor)
                tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to create tracking task for {tracker.name}: {e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for tracker, result in zip(self.trackers, results):
                if isinstance(result, Exception):
                    logger.error(f"Tracker {tracker.name} failed: {result}")
                else:
                    logger.debug(f"Tracker {tracker.name} succeeded")
