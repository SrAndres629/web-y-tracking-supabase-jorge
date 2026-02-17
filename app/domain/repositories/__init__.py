"""
📦 Repository Interfaces (Ports).

Estas interfaces definen los contratos de persistencia.
La infraestructura las implementa (PostgreSQL, SQLite, Memory).

Patrón Repository:
- Abstrae la persistencia del dominio
- Permite cambiar DB sin tocar lógica de negocio
- Facilita testing con implementaciones fake
"""

from app.domain.repositories.event_repo import EventRepository
from app.domain.repositories.lead_repo import LeadRepository
from app.domain.repositories.visitor_repo import VisitorRepository

__all__ = [
    "VisitorRepository",
    "LeadRepository",
    "EventRepository",
]
