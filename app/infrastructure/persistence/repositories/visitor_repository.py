"""
📂 VisitorRepository - Persistencia escalable para visitantes.

Implementa el patrón Repository para desacoplar el dominio de la infraestructura.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.models.values import ExternalId, UTMParams, Email, Phone
from app.domain.repositories.visitor_repo import VisitorRepository as IVisitorRepository
from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


class VisitorRepository(IVisitorRepository):
    """
    Implementación concreta del repositorio de visitantes usando DB nativa.
    """

    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Visitor]:
        """Recupera un visitante por su ID externo."""
        query = "SELECT * FROM visitors WHERE external_id = %s"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")

        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (external_id.value,))
                row = cur.fetchone()
                if not row:
                    return None
                
                # Manual Reconstruct (fragile, but better than dict for Domain)
                # Schema: id(0), ext(1), fbclid(2), ip(3), ua(4), source(5), 
                # utm_s(6), utm_m(7), utm_c(8), utm_t(9), utm_con(10), 
                # email(11), phone(12), created(13)
                
                return Visitor.reconstruct(
                    external_id=external_id,
                    fbclid=row[2],
                    ip_address=row[3],
                    user_agent=row[4],
                    source=VisitorSource(row[5] or "pageview"),
                    utm=UTMParams(
                        source=row[6],
                        medium=row[7],
                        campaign=row[8],
                        term=row[9],
                        content=row[10]
                    ),
                    email=Email(row[11]) if row[11] else None,
                    phone=Phone(row[12]) if row[12] else None,
                    created_at=row[13]
                )
        except Exception as e:
            logger.error(f"❌ Error in get_by_external_id: {e}")
            return None

    async def get_by_fbclid(self, fbclid: str) -> Optional[Visitor]:
        """Busca por FBCLID."""
        query = "SELECT external_id FROM visitors WHERE fbclid = %s LIMIT 1"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")
        
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (fbclid,))
                row = cur.fetchone()
                if row:
                    return await self.get_by_external_id(ExternalId(row[0]))
                return None
        except Exception:
            return None

    async def save(self, visitor: Visitor) -> None:
        """Persiste visitante."""
        # Use legacy-compatible upsert or atomic save
        if db.backend == "postgres":
            query = """
                INSERT INTO visitors (
                    external_id, fbclid, fbp, ip_address, user_agent, source,
                    utm_source, utm_medium, utm_campaign, utm_term, utm_content,
                    email, phone
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_id) DO UPDATE SET
                    fbclid = COALESCE(EXCLUDED.fbclid, visitors.fbclid),
                    fbp = COALESCE(EXCLUDED.fbp, visitors.fbp),
                    email = COALESCE(EXCLUDED.email, visitors.email),
                    phone = COALESCE(EXCLUDED.phone, visitors.phone);
            """
        else:
            query = """
                INSERT OR REPLACE INTO visitors (
                    external_id, fbclid, fbp, ip_address, user_agent, source,
                    utm_source, utm_medium, utm_campaign, utm_term, utm_content,
                    email, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        
        params = (
            visitor.external_id.value,
            visitor.fbclid,
            visitor.fbp,
            visitor.ip_address,
            visitor.user_agent,
            visitor.source.value,
            visitor.utm.source,
            visitor.utm.medium,
            visitor.utm.campaign,
            visitor.utm.term,
            visitor.utm.content,
            visitor.email.value if visitor.email else None,
            visitor.phone.value if visitor.phone else None,
        )

        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
        except Exception as e:
            logger.error(f"❌ Error saving visitor: {e}")

    async def create(self, visitor: Visitor) -> None:
        await self.save(visitor)

    async def update(self, visitor: Visitor) -> None:
        await self.save(visitor)

    async def list_recent(self, limit: int = 50, offset: int = 0) -> List[Visitor]:
        return [] # Simplified

    async def count(self) -> int:
        query = "SELECT COUNT(*) FROM visitors"
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return cur.fetchone()[0]
        except Exception:
            return 0

    async def get_all_visitors(self, limit: int = 50) -> List[Visitor]:
        """Recupera todos los visitantes recientes."""
        query = "SELECT * FROM visitors ORDER BY created_at DESC LIMIT %s"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")
        
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (limit,))
                rows = cur.fetchall()
                return [self._map_row_to_visitor(row, cur) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error in get_all_visitors: {e}")
            return []

    def _map_row_to_visitor(self, row: tuple, cur) -> Visitor:
        """Mapea fila de DB a modelo de dominio Visitor."""
        cols = [col[0] for col in cur.description]
        data = dict(zip(cols, row, strict=False))
        
        return Visitor.reconstruct(
            external_id=ExternalId(data["external_id"]),
            fbclid=data.get("fbclid"),
            fbp=data.get("fbp"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            source=VisitorSource(data.get("source", "pageview")),
            utm=UTMParams(
                source=data.get("utm_source"),
                medium=data.get("utm_medium"),
                campaign=data.get("utm_campaign"),
                term=data.get("utm_term"),
                content=data.get("utm_content")
            ),
            email=Email(data["email"]) if data.get("email") else None,
            phone=Phone(data["phone"]) if data.get("phone") else None,
            created_at=data.get("created_at")
        )

    async def exists(self, external_id: ExternalId) -> bool:
        v = await self.get_by_external_id(external_id)
        return v is not None
