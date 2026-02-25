"""
🎯 SQL Lead Repository Implementation.

Implementación con SQL nativo para crm_leads.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from app import database
from app import sql_queries as queries
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Email, ExternalId, Phone
from app.domain.repositories.lead_repo import LeadRepository

logger = logging.getLogger(__name__)

# Explicit column selection to ensure mapping stability
LEAD_FIELDS = [
    "id",
    "whatsapp_phone",
    "full_name",
    "email",
    "meta_lead_id",
    "fb_click_id",
    "fb_browser_id",
    "status",
    "lead_score",
    "pain_point",
    "service_interest",
    "utm_source",
    "utm_campaign",
    "created_at",
    "updated_at",
    "conversion_sent_to_meta"
]

SELECT_LEAD_SQL = f"SELECT {', '.join(LEAD_FIELDS)} FROM crm_leads"


class SQLLeadRepository(LeadRepository):
    """
    Implementación del repositorio usando SQL nativo.
    Compatible con PostgreSQL y SQLite.
    """

    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                query = f"{SELECT_LEAD_SQL} WHERE id = %s"
                cur.execute(query, (lead_id,))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row)
        except Exception as e:
            logger.exception(f"Error getting lead by id: {e}")
        return None

    async def get_by_phone(self, phone: Phone) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                query = f"{SELECT_LEAD_SQL} WHERE whatsapp_phone = %s"
                cur.execute(query, (str(phone),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row)
        except Exception as e:
            logger.exception(f"Error getting lead by phone: {e}")
        return None

    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                query = f"{SELECT_LEAD_SQL} WHERE fb_browser_id = %s"
                cur.execute(query, (str(external_id),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row)
        except Exception as e:
            logger.exception(f"Error getting lead by external_id: {e}")
        return None

    async def save(self, lead: Lead) -> None:
        if await self.get_by_id(lead.id):
            await self.update(lead)
        else:
            await self.create(lead)

    async def create(self, lead: Lead) -> None:
        try:
            # Reutilizamos la lógica de database.py por ahora o implementamos SQL aquí
            database.upsert_contact_advanced(
                {
                    "phone": str(lead.phone),
                    "name": lead.name,
                    "email": str(lead.email) if lead.email else None,
                    "fbclid": lead.fbclid,
                    "fbp": str(lead.external_id) if lead.external_id else None,
                    "status": lead.status.value,
                    "lead_score": lead.score,
                    "service_interest": lead.service_interest,
                }
            )
        except Exception as e:
            logger.exception(f"Error creating lead: {e}")

    async def update(self, lead: Lead) -> None:
        # Simplificamos usando upsert_contact_advanced
        await self.create(lead)

    async def list_by_status(
        self, status: LeadStatus, limit: int = 50, offset: int = 0
    ) -> List[Lead]:
        # Implementación mínima para dashboard
        return []

    async def list_hot_leads(self, _min_score: int = 70, limit: int = 50) -> List[Lead]:
        return []

    async def list_recent(self, limit: int = 50, offset: int = 0) -> List[Lead]:
        return []

    async def count_by_status(self, status: LeadStatus) -> int:
        return 0

    async def phone_exists(self, phone: Phone) -> bool:
        return await self.get_by_phone(phone) is not None

    def _map_row_to_lead(self, row) -> Lead:
        # Mapped based on LEAD_FIELDS order
        return Lead(
            id=str(row[0]),
            phone=Phone.parse(row[1]).unwrap(),
            name=row[2],
            email=(Email.parse(row[3]).unwrap() if row[3] and Email.parse(row[3]).is_ok else None),
            meta_lead_id=row[4],
            fbclid=row[5],
            external_id=(
                ExternalId.from_string(row[6]).unwrap()
                if row[6] and ExternalId.from_string(row[6]).is_ok
                else None
            ),
            status=LeadStatus(row[7]) if row[7] else LeadStatus.NEW,
            score=row[8] if row[8] is not None else 50,
            pain_point=row[9],
            service_interest=row[10],
            utm_source=row[11],
            utm_campaign=row[12],
            created_at=row[13] if row[13] else datetime.now(timezone.utc),
            updated_at=row[14] if row[14] else datetime.now(timezone.utc),
            sent_to_meta=bool(row[15]) if len(row) > 15 else False,
        )
