"""
🎯 Lead Repository Interface.

Contrato para persistencia de leads.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import ExternalId, Phone


class LeadRepository(ABC):
    """
    Repository para entidad Lead.
    
    Responsabilidades:
    - CRUD de leads
    - Búsquedas por phone, external_id, status
    - Listados filtrados y paginados
    """
    
    @abstractmethod
    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Busca lead por ID (UUID)."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_phone(self, phone: Phone) -> Optional[Lead]:
        """
        Busca lead por teléfono.
        
        Teléfono es único en el sistema.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Lead]:
        """Busca lead asociado a un visitante."""
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, lead: Lead) -> None:
        """
        Persiste lead (create o update).
        
        Upsert basado en ID.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def create(self, lead: Lead) -> None:
        """
        Crea nuevo lead.
        
        Raises:
            DuplicateLeadError: Si el teléfono ya existe.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, lead: Lead) -> None:
        """Actualiza lead existente."""
        raise NotImplementedError
    
    @abstractmethod
    async def list_by_status(
        self,
        status: LeadStatus,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Lead]:
        """Lista leads por estado."""
        raise NotImplementedError
    
    @abstractmethod
    async def list_hot_leads(
        self,
        min_score: int = 70,
        limit: int = 50,
    ) -> List[Lead]:
        """
        Lista leads prioritarios (alto score).
        
        Args:
            min_score: Puntuación mínima
            limit: Cantidad máxima
        """
        raise NotImplementedError
    
    @abstractmethod
    async def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Lead]:
        """Lista leads recientes (ordenados por created_at DESC)."""
        raise NotImplementedError
    
    @abstractmethod
    async def count_by_status(self, status: LeadStatus) -> int:
        """Cuenta leads por estado."""
        raise NotImplementedError
    
    @abstractmethod
    async def phone_exists(self, phone: Phone) -> bool:
        """True si el teléfono ya está registrado."""
        raise NotImplementedError


class LeadNotFoundError(Exception):
    """Lead no encontrado."""
    pass


class DuplicateLeadError(Exception):
    """Lead duplicado (teléfono ya existe)."""
    pass
