"""
📊 Event Repository Implementation.

Implementación de persistencia para eventos de tracking y métricas EMQ.
"""

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
    """Implementación de EventRepository para PostgreSQL y SQLite."""

    async def save(self, event: TrackingEvent) -> None:
        """Guarda evento de tracking."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                query = """
                    INSERT INTO events (
                        event_id, event_name, external_id, source_url, 
                        custom_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                """
                if db.backend == "sqlite":
                    query = query.replace("%s", "?").replace(
                        "ON CONFLICT (event_id) DO NOTHING", "OR IGNORE"
                    )

                cur.execute(
                    query,
                    (
                        str(event.event_id),
                        event.event_name.value,
                        str(event.external_id),
                        event.source_url,
                        json.dumps(event.custom_data),
                        event.created_at,
                    ),
                )

                # 📨 Outbox Pattern: Ensure event delivery via unified transaction
                import uuid

                outbox_id = str(uuid.uuid4())
                outbox_payload = json.dumps(
                    {
                        "event_name": event.event_name.value,
                        "event_id": str(event.event_id),
                        "external_id": str(event.external_id),
                        "source_url": event.source_url,
                        "custom_data": event.custom_data,
                        "created_at": event.created_at.isoformat()
                        if hasattr(event.created_at, "isoformat")
                        else str(event.created_at),
                    }
                )

                if db.backend == "postgres":
                    outbox_query = """
                        INSERT INTO outbox_events (
                            id, aggregate_type, aggregate_id, event_type, payload
                        ) VALUES (%s, %s, %s, %s, %s)
                    """
                else:
                    outbox_query = """
                        INSERT INTO outbox_events (
                            id, aggregate_type, aggregate_id, event_type, payload
                        ) VALUES (?, ?, ?, ?, ?)
                    """

                cur.execute(
                    outbox_query,
                    (
                        outbox_id,
                        "TrackingEvent",
                        str(event.event_id),
                        "TRACKING_EVENT_SAVED",
                        outbox_payload,
                    ),
                )
        except Exception:
            logger.exception("❌ Error saving event to database")

    async def get_by_id(self, event_id: EventId) -> Optional[TrackingEvent]:
        """Busca evento por ID."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                query = "SELECT * FROM events WHERE event_id = %s"
                if db.backend == "sqlite":
                    query = query.replace("%s", "?")

                cur.execute(query, (str(event_id),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_event(row, cur)
            return None
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return None

    async def exists(self, event_id: EventId) -> bool:
        """Verifica existencia."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                query = "SELECT 1 FROM events WHERE event_id = %s LIMIT 1"
                if db.backend == "sqlite":
                    query = query.replace("%s", "?")

                cur.execute(query, (str(event_id),))
                return cur.fetchone() is not None
        except Exception:
            return False

    def _map_row_to_event(self, row, cur) -> TrackingEvent:
        """Mapea fila de DB a modelo de dominio."""
        cols = [col[0] for col in cur.description]
        data = dict(zip(cols, row, strict=False))

        return TrackingEvent(
            event_name=EventName(data["event_name"]),
            event_id=EventId(data["event_id"]),
            external_id=ExternalId(data["external_id"]),
            source_url=data["source_url"],
            custom_data=json.loads(data["custom_data"])
            if isinstance(data["custom_data"], str)
            else data["custom_data"],
            created_at=data["created_at"]
            if isinstance(data["created_at"], datetime)
            else datetime.fromisoformat(data["created_at"]),
        )

    # Simplified EMQ methods for analytics
    async def save_emq_score(
        self,
        client_id: Optional[str],
        event_name: str,
        score: float,
        payload_size: int,
        has_pii: bool,
    ) -> None:
        """Guarda score EMQ para monitoreo."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                query = """
                    INSERT INTO emq_scores (client_id, event_name, score, payload_size, has_pii)
                    VALUES (%s, %s, %s, %s, %s)
                """
                if db.backend == "sqlite":
                    query = query.replace("%s", "?")

                cur.execute(
                    query, (client_id, event_name, score, payload_size, has_pii)
                )
        except Exception as e:
            logger.warning(f"⚠️ Error saving EMQ score: {e}")

    async def get_emq_stats(self, limit: int = 20) -> List[dict]:
        """Obtiene estadísticas EMQ recientes."""
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                query = """
                    SELECT event_name, AVG(score) as avg_score, COUNT(*) as count, MAX(created_at) as last_seen
                    FROM emq_scores
                    GROUP BY event_name
                    ORDER BY last_seen DESC
                    LIMIT %s
                """
                if db.backend == "sqlite":
                    query = query.replace("%s", "?")

                cur.execute(query, (limit,))
                rows = cur.fetchall()

                results = []
                for row in rows:
                    results.append(
                        {
                            "event_name": row[0],
                            "avg_score": round(row[1], 2),
                            "count": row[2],
                            "last_seen": row[3],
                        }
                    )
                return results
        except Exception:
            return []

    # Implement other abstract methods as needed (stubs for now to satisfy interface)
    async def list_by_visitor(
        self, external_id: ExternalId, limit: int = 100
    ) -> List[TrackingEvent]:
        return []

    async def list_by_visitor_and_type(
        self, external_id: ExternalId, event_name: EventName, limit: int = 50
    ) -> List[TrackingEvent]:
        return []

    async def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        event_name: Optional[EventName] = None,
        limit: int = 1000,
    ) -> List[TrackingEvent]:
        return []

    async def count_by_visitor(self, external_id: ExternalId) -> int:
        return 0

    async def count_by_type_and_date(
        self, event_name: EventName, date: datetime
    ) -> int:
        return 0
