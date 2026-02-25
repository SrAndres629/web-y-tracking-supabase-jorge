"""
📊 Event Repository Implementation.

PostgreSQL implementation para persistencia de eventos.
Uses SQLAlchemy Core for async implementation and cross-db compatibility.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import and_, desc, func, insert, select
from sqlalchemy.exc import IntegrityError

from app.domain.models.events import EventName, TrackingEvent
from app.domain.models.values import EventId, ExternalId
from app.domain.repositories.event_repo import EventRepository
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.tables import events_table

logger = logging.getLogger(__name__)


class PostgreSQLEventRepository(EventRepository):
    """Implementación PostgreSQL del repositorio de eventos."""

    def __init__(self):
        self._db = db

    def _row_to_entity(self, row: Any) -> TrackingEvent:
        """Convierte fila de DB a entidad."""
        # Columns: id, event_id, event_name, external_id, event_time, source_url, custom_data
        # Indices: 0,  1,        2,          3,           4,          5,          6

        # Handle custom_data
        custom_data_raw = row[6]
        custom_data = {}
        if custom_data_raw is not None:
            if isinstance(custom_data_raw, str):
                try:
                    custom_data = json.loads(custom_data_raw)
                except json.JSONDecodeError:
                    custom_data = {}
            elif isinstance(custom_data_raw, dict):
                custom_data = custom_data_raw
            # If it's already a dict (e.g. from JSON type), use it.

        return TrackingEvent.reconstruct(
            event_id=EventId(row[1]),
            event_name=EventName(row[2]),
            external_id=ExternalId(row[3]),
            timestamp=row[4] if isinstance(row[4], datetime) else datetime.utcnow(),
            source_url=row[5],
            custom_data=custom_data,
        )

    async def save(self, event: TrackingEvent) -> None:
        """Inserta evento (idempotente)."""
        if await self.exists(event.event_id):
            logger.debug(f"Event already exists: {event.event_id}")
            return

        stmt = insert(events_table).values(
            event_id=event.event_id.value,
            event_name=event.event_name.value,
            external_id=event.external_id.value,
            event_time=event.timestamp,
            source_url=event.source_url,
            custom_data=event.custom_data,
            utm_source=event.utm.source,
            utm_medium=event.utm.medium,
            utm_campaign=event.utm.campaign,
        )

        try:
            async with self._db.async_connection() as conn:
                await conn.execute(stmt)
        except IntegrityError:
            logger.debug(f"Event collision (race condition): {event.event_id}")
            # Ignore duplicate
            pass

    async def get_by_id(self, event_id: EventId) -> Optional[TrackingEvent]:
        """Busca evento por ID."""
        stmt = select(
            events_table.c.id,
            events_table.c.event_id,
            events_table.c.event_name,
            events_table.c.external_id,
            events_table.c.event_time,
            events_table.c.source_url,
            events_table.c.custom_data,
        ).where(events_table.c.event_id == event_id.value)

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            row = result.fetchone()
            return self._row_to_entity(row) if row else None

    async def list_by_visitor(
        self,
        external_id: ExternalId,
        limit: int = 100,
    ) -> List[TrackingEvent]:
        """Lista eventos de un visitante."""
        stmt = (
            select(
                events_table.c.id,
                events_table.c.event_id,
                events_table.c.event_name,
                events_table.c.external_id,
                events_table.c.event_time,
                events_table.c.source_url,
                events_table.c.custom_data,
            )
            .where(events_table.c.external_id == external_id.value)
            .order_by(desc(events_table.c.event_time))
            .limit(limit)
        )

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            rows = result.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def list_by_visitor_and_type(
        self,
        external_id: ExternalId,
        event_name: EventName,
        limit: int = 50,
    ) -> List[TrackingEvent]:
        """Lista eventos de un tipo específico."""
        stmt = (
            select(
                events_table.c.id,
                events_table.c.event_id,
                events_table.c.event_name,
                events_table.c.external_id,
                events_table.c.event_time,
                events_table.c.source_url,
                events_table.c.custom_data,
            )
            .where(
                and_(
                    events_table.c.external_id == external_id.value,
                    events_table.c.event_name == event_name.value,
                )
            )
            .order_by(desc(events_table.c.event_time))
            .limit(limit)
        )

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            rows = result.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        event_name: Optional[EventName] = None,
        limit: int = 1000,
    ) -> List[TrackingEvent]:
        """Lista eventos en rango de fechas."""
        stmt = select(
            events_table.c.id,
            events_table.c.event_id,
            events_table.c.event_name,
            events_table.c.external_id,
            events_table.c.event_time,
            events_table.c.source_url,
            events_table.c.custom_data,
        ).where(events_table.c.event_time.between(start, end))

        if event_name:
            stmt = stmt.where(events_table.c.event_name == event_name.value)

        stmt = stmt.order_by(desc(events_table.c.event_time)).limit(limit)

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            rows = result.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def exists(self, event_id: EventId) -> bool:
        """Verifica si evento existe."""
        stmt = select(1).where(events_table.c.event_id == event_id.value).limit(1)

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            return result.fetchone() is not None

    async def count_by_visitor(self, external_id: ExternalId) -> int:
        """Cuenta eventos de un visitante."""
        stmt = select(func.count()).where(
            events_table.c.external_id == external_id.value
        )

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            return result.scalar() or 0

    async def count_by_type_and_date(
        self,
        event_name: EventName,
        date: datetime,
    ) -> int:
        """Cuenta eventos de un tipo en fecha específica."""
        stmt = select(func.count()).where(
            and_(
                events_table.c.event_name == event_name.value,
                func.date(events_table.c.event_time) == func.date(date),
            )
        )

        async with self._db.async_connection() as conn:
            result = await conn.execute(stmt)
            return result.scalar() or 0
