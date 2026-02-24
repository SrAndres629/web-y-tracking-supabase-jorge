"""
🔍 Query Handlers - Casos de uso de lectura (CQRS).

Las queries son operaciones de solo lectura, optimizadas para consulta.
No modifican estado.
"""

from app.application.queries.get_visitor import GetVisitorHandler, GetVisitorQuery
from app.application.queries.list_visitors import ListVisitorsHandler, ListVisitorsQuery

__all__ = [
    "GetVisitorHandler",
    "GetVisitorQuery",
    "ListVisitorsHandler",
    "ListVisitorsQuery",
]
