"""
📋 List Visitors Query.

Consulta: Listar visitantes recientes (para admin).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.core.result import Result
from app.domain.repositories.visitor_repo import VisitorRepository
from app.application.dto.visitor_dto import VisitorResponse, VisitorListResponse


@dataclass(frozen=True)
class ListVisitorsQuery:
    """Input para la query."""
    limit: int = 50
    offset: int = 0


class ListVisitorsHandler:
    """Handler para listar visitantes."""
    
    def __init__(self, visitor_repo: VisitorRepository):
        self.visitor_repo = visitor_repo
    
    async def handle(self, query: ListVisitorsQuery) -> Result[VisitorListResponse, str]:
        """Lista visitantes recientes."""
        try:
            # Validar parámetros
            limit = min(max(query.limit, 1), 100)  # 1-100
            offset = max(query.offset, 0)
            
            # Consultar
            visitors = await self.visitor_repo.list_recent(limit=limit, offset=offset)
            total = await self.visitor_repo.count()
            
            # Mapear
            items = [
                VisitorResponse(
                    external_id=v.external_id.value,
                    fbclid=v.fbclid,
                    fbp=v.fbp,
                    source=v.source.value,
                    visit_count=v.visit_count,
                    created_at=v.created_at,
                    last_seen=v.last_seen,
                )
                for v in visitors
            ]
            
            return Result.ok(VisitorListResponse(
                items=items,
                total=total,
                limit=limit,
                offset=offset,
            ))
            
        except Exception as e:
            return Result.err(str(e))
