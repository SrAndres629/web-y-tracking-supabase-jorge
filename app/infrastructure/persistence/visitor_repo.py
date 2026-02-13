"""
👤 Visitor Repository Implementation.

PostgreSQL implementation con SQLite fallback.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from datetime import datetime

from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.models.values import ExternalId, UTMParams, GeoLocation
from app.domain.repositories.visitor_repo import VisitorRepository, DuplicateVisitorError
from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


class PostgreSQLVisitorRepository(VisitorRepository):
    """Implementación PostgreSQL del repositorio de visitantes."""
    
    def __init__(self):
        self._db = db
    
    def _row_to_entity(self, row: tuple) -> Visitor:
        """Convierte fila de DB a entidad de dominio."""
        # Asumiendo columnas: id, external_id, fbclid, fbp, ip_address, user_agent, 
        # source, utm_source, utm_medium, utm_campaign, country, city, created_at, last_seen, visit_count
        return Visitor.reconstruct(
            external_id=ExternalId(row[1]),
            fbclid=row[2],
            fbp=row[3],
            ip_address=row[4],
            user_agent=row[5],
            source=VisitorSource(row[6]) if row[6] else VisitorSource.PAGEVIEW,
            utm=UTMParams.from_dict({
                "utm_source": row[7],
                "utm_medium": row[8],
                "utm_campaign": row[9],
            }),
            geo=GeoLocation(
                country=row[10],
                city=row[11],
            ),
            created_at=row[12] if isinstance(row[12], datetime) else datetime.utcnow(),
            last_seen=row[13] if isinstance(row[13], datetime) else datetime.utcnow(),
            visit_count=row[14] if len(row) > 14 else 1,
        )
    
    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Visitor]:
        """Busca visitante por external_id."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, external_id, fbclid, fbp, ip_address, user_agent,
                       source, utm_source, utm_medium, utm_campaign,
                       country, city, created_at, last_seen, visit_count
                FROM visitors
                WHERE external_id = %s
                """,
                (external_id.value,)
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
    
    async def get_by_fbclid(self, fbclid: str) -> Optional[Visitor]:
        """Busca visitante por fbclid."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, external_id, fbclid, fbp, ip_address, user_agent,
                       source, utm_source, utm_medium, utm_campaign,
                       country, city, created_at, last_seen, visit_count
                FROM visitors
                WHERE fbclid = %s
                ORDER BY last_seen DESC
                LIMIT 1
                """,
                (fbclid,)
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
    
    async def save(self, visitor: Visitor) -> None:
        """Upsert de visitante."""
        if await self.exists(visitor.external_id):
            await self.update(visitor)
        else:
            await self.create(visitor)
    
    async def create(self, visitor: Visitor) -> None:
        """Inserta nuevo visitante."""
        if await self.exists(visitor.external_id):
            raise DuplicateVisitorError(f"Visitor {visitor.external_id} already exists")
        
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO visitors (
                    external_id, fbclid, fbp, ip_address, user_agent,
                    source, utm_source, utm_medium, utm_campaign,
                    country, city, created_at, last_seen, visit_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    visitor.external_id.value,
                    visitor.fbclid,
                    visitor.fbp,
                    visitor.ip_address,
                    visitor.user_agent,
                    visitor.source.value,
                    visitor.utm.source,
                    visitor.utm.medium,
                    visitor.utm.campaign,
                    visitor.geo.country,
                    visitor.geo.city,
                    visitor.created_at,
                    visitor.last_seen,
                    visitor.visit_count,
                )
            )
    
    async def update(self, visitor: Visitor) -> None:
        """Actualiza visitante existente."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE visitors SET
                    fbclid = %s,
                    fbp = %s,
                    last_seen = %s,
                    visit_count = %s,
                    country = %s,
                    city = %s
                WHERE external_id = %s
                """,
                (
                    visitor.fbclid,
                    visitor.fbp,
                    visitor.last_seen,
                    visitor.visit_count,
                    visitor.geo.country,
                    visitor.geo.city,
                    visitor.external_id.value,
                )
            )
    
    async def list_recent(self, limit: int = 50, offset: int = 0) -> List[Visitor]:
        """Lista visitantes recientes."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, external_id, fbclid, fbp, ip_address, user_agent,
                       source, utm_source, utm_medium, utm_campaign,
                       country, city, created_at, last_seen, visit_count
                FROM visitors
                ORDER BY last_seen DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    async def count(self) -> int:
        """Cuenta total de visitantes."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM visitors")
            row = cursor.fetchone()
            return row[0] if row else 0
    
    async def exists(self, external_id: ExternalId) -> bool:
        """Verifica si existe."""
        async with self._db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM visitors WHERE external_id = %s LIMIT 1",
                (external_id.value,)
            )
            return cursor.fetchone() is not None
