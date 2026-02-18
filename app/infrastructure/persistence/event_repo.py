"""
📊 Event Repository Implementation.

PostgreSQL implementation para persistencia de eventos.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import List, Optional

from app.domain.models.events import EventName, TrackingEvent
from app.domain.models.values import EventId, ExternalId
from app.domain.repositories.event_repo import EventRepository
from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


class PostgreSQLEventRepository(EventRepository):
    """Implementación PostgreSQL del repositorio de eventos."""

    def __init__(self):
        self._db = db

    def _row_to_entity(self, row: tuple) -> TrackingEvent:
        """Convierte fila de DB a entidad."""
        return TrackingEvent.reconstruct(
            event_id=EventId(row[1]),
            event_name=EventName(row[2]),
            external_id=ExternalId(row[3]),
            timestamp=row[4] if isinstance(row[4], datetime) else datetime.utcnow(),
            source_url=row[5],
            custom_data=json.loads(row[6]) if row[6] else {},
        )

    async def save(self, event: TrackingEvent) -> None:
        """Inserta evento (idempotente)."""
        if await self.exists(event.event_id):
            logger.debug(f"Event already exists: {event.event_id}")
            return

        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (
                    event_id, event_name, external_id, event_time,
                    source_url, custom_data, utm_source, utm_medium, utm_campaign
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (
                    event.event_id.value,
                    event.event_name.value,
                    event.external_id.value,
                    event.timestamp,
                    event.source_url,
                    json.dumps(event.custom_data),
                    event.utm.source,
                    event.utm.medium,
                    event.utm.campaign,
                ),
            )

    async def get_by_id(self, event_id: EventId) -> Optional[TrackingEvent]:
        """Busca evento por ID."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, event_id, event_name, external_id, event_time,
                       source_url, custom_data
                FROM events
                WHERE event_id = %s
                """,
                (event_id.value,),
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    async def list_by_visitor(
        self,
        external_id: ExternalId,
        limit: int = 100,
    ) -> List[TrackingEvent]:
        """Lista eventos de un visitante."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, event_id, event_name, external_id, event_time,
                       source_url, custom_data
                FROM events
                WHERE external_id = %s
                ORDER BY event_time DESC
                LIMIT %s
                """,
                (external_id.value, limit),
            )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def list_by_visitor_and_type(
        self,
        external_id: ExternalId,
        event_name: EventName,
        limit: int = 50,
    ) -> List[TrackingEvent]:
        """Lista eventos de un tipo específico."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, event_id, event_name, external_id, event_time,
                       source_url, custom_data
                FROM events
                WHERE external_id = %s AND event_name = %s
                ORDER BY event_time DESC
                LIMIT %s
                """,
                (external_id.value, event_name.value, limit),
            )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        event_name: Optional[EventName] = None,
        limit: int = 1000,
    ) -> List[TrackingEvent]:
        """Lista eventos en rango de fechas."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            if event_name:
                cursor.execute(
                    """
                    SELECT id, event_id, event_name, external_id, event_time,
                           source_url, custom_data
                    FROM events
                    WHERE event_time BETWEEN %s AND %s AND event_name = %s
                    ORDER BY event_time DESC
                    LIMIT %s
                    """,
                    (start, end, event_name.value, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, event_id, event_name, external_id, event_time,
                           source_url, custom_data
                    FROM events
                    WHERE event_time BETWEEN %s AND %s
                    ORDER BY event_time DESC
                    LIMIT %s
                    """,
                    (start, end, limit),
                )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    async def exists(self, event_id: EventId) -> bool:
        """Verifica si evento existe."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM events WHERE event_id = %s LIMIT 1", (event_id.value,))
            return cursor.fetchone() is not None

    async def count_by_visitor(self, external_id: ExternalId) -> int:
        """Cuenta eventos de un visitante."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM events WHERE external_id = %s",
                (external_id.value,),
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    async def count_by_type_and_date(
        self,
        event_name: EventName,
        date: datetime,
    ) -> int:
        """Cuenta eventos de un tipo en fecha específica."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE event_name = %s
                AND DATE(event_time) = DATE(%s)
                """,
                (event_name.value, date),
            )
            row = cursor.fetchone()
            return row[0] if row else 0
