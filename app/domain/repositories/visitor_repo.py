"""
👤 Visitor Repository Interface.

Contrato para persistencia de visitantes.
Implementaciones: PostgreSQLVisitorRepository, SQLiteVisitorRepository, InMemoryVisitorRepository
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.visitor import ExternalId, Visitor


class VisitorRepository(ABC):
    """
    Repository para entidad Visitor.

    Responsabilidades:
    - CRUD de visitantes
    - Búsquedas por external_id, fbclid
    - Listados paginados

    No contiene lógica de negocio, solo persistencia.
    """

    @abstractmethod
    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Visitor]:
        """
        Busca visitante por ID externo.

        Returns:
            Visitor si existe, None si no encontrado.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_fbclid(self, fbclid: str) -> Optional[Visitor]:
        """
        Busca visitante por FBCLID (Facebook Click ID).

        Usado para reconectar sesiones.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, visitor: Visitor) -> None:
        """
        Persiste visitante (create o update).

        Si ya existe (mismo external_id), actualiza.
        Si no existe, crea nuevo.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, visitor: Visitor) -> None:
        """
        Crea nuevo visitante.

        Raises:
            DuplicateError: Si ya existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, visitor: Visitor) -> None:
        """
        Actualiza visitante existente.

        Raises:
            NotFoundError: Si no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Visitor]:
        """
        Lista visitantes recientes (ordenados por last_seen DESC).

        Args:
            limit: Cantidad máxima
            offset: Para paginación
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Cuenta total de visitantes."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, external_id: ExternalId) -> bool:
        """True si el visitante existe."""
        raise NotImplementedError


class VisitorNotFoundError(Exception):
    """Visitante no encontrado."""

    pass


class DuplicateVisitorError(Exception):
    """Visitante duplicado."""

    pass
