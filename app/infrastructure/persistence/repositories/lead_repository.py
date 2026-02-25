"""
📂 LeadRepository - Persistencia escalable para Leads (CRM).

Implementación concreta del repositorio de leads usando DB nativa.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Email, ExternalId, Phone
from app.domain.repositories.lead_repo import LeadRepository as ILeadRepository
from app.infrastructure.persistence.database import db

logger = logging.getLogger(__name__)


class LeadRepository(ILeadRepository):
    """
    Implementación nativa de LeadRepository.
    """

    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Recupera lead por ID."""
        query = "SELECT * FROM crm_leads WHERE id = %s"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")
        
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (lead_id,))
                row = cur.fetchone()
                return self._map_row_to_lead(row, cur) if row else None
        except Exception as e:
            logger.error(f"❌ Error in get_by_id: {e}")
            return None

    async def get_by_phone(self, phone: Phone) -> Optional[Lead]:
        """Recupera lead por teléfono."""
        query = "SELECT * FROM crm_leads WHERE phone = %s"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")
        
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (str(phone),))
                row = cur.fetchone()
                return self._map_row_to_lead(row, cur) if row else None
        except Exception as e:
            logger.error(f"❌ Error in get_by_phone: {e}")
            return None

    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Lead]:
        """Recupera lead por ID de visitante."""
        query = "SELECT * FROM crm_leads WHERE external_id = %s"
        if db.backend == "sqlite":
            query = query.replace("%s", "?")
        
        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (external_id.value,))
                row = cur.fetchone()
                return self._map_row_to_lead(row, cur) if row else None
        except Exception:
            return None

    async def save(self, lead: Lead) -> None:
        """Persiste lead (upsert)."""
        if db.backend == "postgres":
            query = """
                INSERT INTO crm_leads (
                    id, phone, name, email,
                    fbclid, external_id, meta_lead_id,
                    status, score, service_interest, pain_point,
                    utm_source, utm_campaign, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    phone = EXCLUDED.phone,
                    name = COALESCE(EXCLUDED.name, crm_leads.name),
                    email = COALESCE(EXCLUDED.email, crm_leads.email),
                    status = EXCLUDED.status,
                    score = EXCLUDED.score,
                    pain_point = EXCLUDED.pain_point,
                    updated_at = NOW();
            """
        else:
            query = """
                INSERT OR REPLACE INTO crm_leads (
                    id, phone, name, email,
                    fbclid, external_id, meta_lead_id,
                    status, score, service_interest, pain_point,
                    utm_source, utm_campaign, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        
        params = (
            lead.id,
            str(lead.phone),
            lead.name,
            str(lead.email) if lead.email else None,
            lead.fbclid,
            str(lead.external_id) if lead.external_id else None,
            lead.meta_lead_id,
            lead.status.value,
            lead.score,
            lead.service_interest,
            lead.pain_point,
            lead.utm_source,
            lead.utm_campaign,
            lead.created_at.isoformat() if hasattr(lead.created_at, "isoformat") else str(lead.created_at),
            lead.updated_at.isoformat() if hasattr(lead.updated_at, "isoformat") else str(lead.updated_at),
        )
        if db.backend == "postgres":
            params = params[:-1]

        try:
            async with db.connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
        except Exception as e:
            logger.error(f"❌ Error saving lead: {e}")

    async def create(self, lead: Lead) -> None:
        await self.save(lead)

    async def update(self, lead: Lead) -> None:
        await self.save(lead)

    async def list_by_status(self, status: LeadStatus, limit: int = 50, offset: int = 0) -> List[Lead]:
        return []

    async def list_hot_leads(self, _min_score: int = 70, limit: int = 50) -> List[Lead]:
        return []

    async def list_recent(self, limit: int = 50, offset: int = 0) -> List[Lead]:
        return []

    async def count_by_status(self, status: LeadStatus) -> int:
        return 0

    async def phone_exists(self, phone: Phone) -> bool:
        l = await self.get_by_phone(phone)
        return l is not None

    def _map_row_to_lead(self, row: tuple, cur) -> Lead:
        """Mapea fila de DB a modelo de dominio de forma robusta."""
        cols = [col[0] for col in cur.description]
        data = dict(zip(cols, row, strict=False))
        
        return Lead(
            id=data["id"],
            phone=Phone.parse(data["phone"]).unwrap() if data["phone"] else None,
            name=data["name"],
            email=Email.parse(data["email"]).unwrap() if data["email"] else None,
            meta_lead_id=data.get("meta_lead_id"),
            fbclid=data.get("fbclid"),
            external_id=ExternalId.from_string(data["external_id"]).unwrap() if data.get("external_id") else None,
            utm_source=data.get("utm_source"),
            status=LeadStatus(data.get("status", "new")),
            score=data.get("score", 50),
            service_interest=data.get("service_interest"),
            pain_point=data.get("pain_point"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
