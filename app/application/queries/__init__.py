"""
🔍 Query Handlers - Casos de uso de lectura (CQRS).

Las queries son operaciones de solo lectura, optimizadas para consulta.
No modifican estado.
"""

from app.application.queries.get_visitor import GetVisitorQuery, GetVisitorHandler
from app.application.queries.list_visitors import ListVisitorsQuery, ListVisitorsHandler
from app.application.queries.get_content import GetContentQuery, GetContentHandler

__all__ = [
    "GetVisitorQuery",
    "GetVisitorHandler",
    "ListVisitorsQuery",
    "ListVisitorsHandler",
    "GetContentQuery",
    "GetContentHandler",
]
