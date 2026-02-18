"""
👤 Create Visitor Command.

Caso de uso: Registrar nuevo visitante.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.application.dto.visitor_dto import VisitorResponse
from app.core.result import Result
from app.domain.models.values import UTMParams
from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.repositories.visitor_repo import VisitorRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateVisitorCommand:
    """Input para crear visitante."""

    ip_address: str
    user_agent: str
    fbclid: str | None = None
    fbp: str | None = None
    source: str = "pageview"
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None


class CreateVisitorHandler:
    """Handler para crear visitantes."""

    def __init__(self, visitor_repo: VisitorRepository):
        self.visitor_repo = visitor_repo

    async def handle(self, cmd: CreateVisitorCommand) -> Result[VisitorResponse, str]:
        """
        Crea o recupera visitante.

        Si ya existe (misma IP+UA), retorna existente.
        """
        try:
            # Crear entidad de dominio
            visitor = Visitor.create(
                ip=cmd.ip_address,
                user_agent=cmd.user_agent,
                fbclid=cmd.fbclid,
                fbp=cmd.fbp,
                source=VisitorSource(cmd.source) if cmd.source else VisitorSource.PAGEVIEW,
                utm=UTMParams.from_dict(
                    {
                        "utm_source": cmd.utm_source,
                        "utm_medium": cmd.utm_medium,
                        "utm_campaign": cmd.utm_campaign,
                    }
                ),
            )

            # Verificar si existe
            existing = await self.visitor_repo.get_by_external_id(visitor.external_id)
            if existing:
                # Actualizar visita
                existing.record_visit()
                if cmd.fbclid:
                    existing.update_fbclid(cmd.fbclid)
                await self.visitor_repo.update(existing)

                logger.info(f"🔄 Returning visitor: {existing.external_id}")
                return Result.ok(self._to_response(existing))

            # Crear nuevo
            await self.visitor_repo.create(visitor)
            logger.info(f"✅ New visitor: {visitor.external_id}")

            return Result.ok(self._to_response(visitor))

        except Exception as e:
            logger.exception(f"❌ Error creating visitor: {e}")
            return Result.err(str(e))

    def _to_response(self, visitor: Visitor) -> VisitorResponse:
        return VisitorResponse(
            external_id=visitor.external_id.value,
            fbclid=visitor.fbclid,
            fbp=visitor.fbp,
            source=visitor.source.value,
            visit_count=visitor.visit_count,
            created_at=visitor.created_at,
            last_seen=visitor.last_seen,
        )
