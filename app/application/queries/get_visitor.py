"""
👤 Get Visitor Query.

Consulta: Buscar visitante por ID.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.result import Result
from app.domain.models.values import ExternalId
from app.domain.repositories.visitor_repo import VisitorRepository
from app.application.dto.visitor_dto import VisitorResponse


@dataclass(frozen=True)
class GetVisitorQuery:
    """Input para la query."""
    external_id: str


class GetVisitorHandler:
    """Handler para buscar visitante."""
    
    def __init__(self, visitor_repo: VisitorRepository):
        self.visitor_repo = visitor_repo
    
    async def handle(self, query: GetVisitorQuery) -> Result[Optional[VisitorResponse], str]:
        """Busca visitante por external_id."""
        try:
            # Validar ID
            id_result = ExternalId.from_string(query.external_id)
            if id_result.is_err:
                return Result.err(f"Invalid external_id: {id_result.unwrap_err()}")
            
            external_id = id_result.unwrap()
            
            # Buscar
            visitor = await self.visitor_repo.get_by_external_id(external_id)
            if not visitor:
                return Result.ok(None)
            
            # Mapear a DTO
            return Result.ok(VisitorResponse(
                external_id=visitor.external_id.value,
                fbclid=visitor.fbclid,
                fbp=visitor.fbp,
                source=visitor.source.value,
                visit_count=visitor.visit_count,
                created_at=visitor.created_at,
                last_seen=visitor.last_seen,
            ))
            
        except Exception as e:
            return Result.err(str(e))
