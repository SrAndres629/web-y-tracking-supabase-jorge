"""
🎯 SQL Lead Repository Implementation.

Implementación con SQL nativo para crm_leads.
"""

import logging
from datetime import datetime
from typing import Any, List, Optional

from app import database
from app import sql_queries as queries
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Email, ExternalId, Phone
from app.domain.repositories.lead_repo import LeadRepository

logger = logging.getLogger(__name__)


class SQLLeadRepository(LeadRepository):
    """
    Implementación del repositorio usando SQL nativo.
    Compatible con PostgreSQL y SQLite.
    """

    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                cur.execute(queries.SELECT_LEAD_BY_ID, (lead_id,))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row)
        except Exception as e:
            logger.exception(f"Error getting lead by id: {e}")
        return None

    async def get_by_phone(self, phone: Phone) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                cur.execute(queries.SELECT_LEAD_BY_PHONE, (str(phone),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row)
        except Exception as e:
            logger.exception(f"Error getting lead by phone: {e}")
        return None

    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                # Note: This query still uses SELECT * so it might fail if we don't update it too.
                # However, for now we leave it as is or update it to use SELECT_LEAD_COLS but filtering by fb_browser_id?
                # The original query was SELECT * FROM crm_leads WHERE fb_browser_id = %s
                # We should update it to maintain consistency.
                query = f"SELECT {queries.SELECT_LEAD_COLS} FROM crm_leads WHERE fb_browser_id = %s"
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
        # Based on SELECT_LEAD_COLS in sql_queries.py:
        # 0: id, 1: whatsapp_phone, 2: full_name, 3: email, 4: meta_lead_id,
        # 5: profile_pic_url, 6: fb_click_id, 7: fb_browser_id,
        # 8-12: utm_*, 13: web_visit_count, 14: sent_to_meta,
        # 15: status, 16: lead_score, 17: pain_point, 18: service_interest,
        # 19: created_at, 20: updated_at

        return Lead(
            id=str(row[0]),
            phone=Phone.parse(row[1]).unwrap(),
            name=row[2],
            email=(Email.parse(row[3]).unwrap() if row[3] and Email.parse(row[3]).is_ok else None),
            meta_lead_id=row[4],
            fbclid=row[6],
            external_id=(
                ExternalId.from_string(row[7]).unwrap()
                if row[7] and ExternalId.from_string(row[7]).is_ok
                else None
            ),
            utm_source=row[8],
            utm_campaign=row[10],
            sent_to_meta=bool(row[14]) if row[14] is not None else False,
            status=LeadStatus(row[15]) if row[15] else LeadStatus.NEW,
            score=row[16] if row[16] is not None else 50,
            pain_point=row[17],
            service_interest=row[18],
            created_at=self._parse_datetime(row[19]) if len(row) > 19 else datetime.now(),
            updated_at=self._parse_datetime(row[20]) if len(row) > 20 else datetime.now(),
        )

    def _parse_datetime(self, val: Any) -> datetime:
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                # Handle ISO format (with T or space)
                return datetime.fromisoformat(val.replace(" ", "T"))
            except ValueError:
                pass
        return datetime.now()
