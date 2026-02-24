"""
🎯 SQL Lead Repository Implementation.

Implementación con SQL nativo para crm_leads.
"""

import logging
from typing import List, Optional

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
                    return self._map_row_to_lead(row, cur.description)
        except Exception as e:
            logger.exception(f"Error getting lead by id: {e}")
        return None

    async def get_by_phone(self, phone: Phone) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                cur.execute(queries.SELECT_LEAD_BY_PHONE, (str(phone),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row, cur.description)
        except Exception as e:
            logger.exception(f"Error getting lead by phone: {e}")
        return None

    async def get_by_external_id(self, external_id: ExternalId) -> Optional[Lead]:
        try:
            with database.get_cursor() as cur:
                cur.execute(queries.SELECT_LEAD_BY_EXTERNAL_ID, (str(external_id),))
                row = cur.fetchone()
                if row:
                    return self._map_row_to_lead(row, cur.description)
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
                    "id": lead.id,
                    "phone": str(lead.phone),
                    "name": lead.name,
                    "email": str(lead.email) if lead.email else None,
                    "fbclid": lead.fbclid,
                    "fbp": str(lead.external_id) if lead.external_id else None,
                    "status": lead.status.value,
                    "lead_score": lead.score,
                    "pain_point": lead.pain_point,
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

    def _map_row_to_lead(self, row: tuple, description: Optional[tuple]) -> Lead:
        """
        Mapea una fila de la base de datos a la entidad Lead de forma robusta.
        Usa la descripción del cursor para mapear por nombre de columna.
        """
        if not description:
            # Fallback a mapeo por índice si no hay descripción (no debería ocurrir)
            return Lead(
                id=str(row[0]),
                phone=Phone.parse(row[1]).unwrap(),
                name=row[2] if len(row) > 2 else None,
                status=LeadStatus.NEW,
            )

        columns = [col[0] for col in description]
        data = dict(zip(columns, row, strict=False))

        # Parse Contact info
        phone_res = Phone.parse(data.get("whatsapp_phone"))
        phone = phone_res.unwrap() if phone_res.is_ok else Phone(number=data.get("whatsapp_phone", ""))

        email = None
        if data.get("email"):
            email_res = Email.parse(data.get("email"))
            if email_res.is_ok:
                email = email_res.unwrap()

        # Parse External ID
        external_id = None
        if data.get("fb_browser_id"):
            ext_res = ExternalId.from_string(data.get("fb_browser_id"))
            if ext_res.is_ok:
                external_id = ext_res.unwrap()

        # Parse Status
        status_val = data.get("status", "new")
        try:
            status = LeadStatus(status_val)
        except (ValueError, KeyError):
            status = LeadStatus.NEW

        return Lead(
            id=str(data.get("id")),
            phone=phone,
            name=data.get("full_name"),
            email=email,
            external_id=external_id,
            meta_lead_id=data.get("meta_lead_id"),
            fbclid=data.get("fb_click_id"),
            status=status,
            score=data.get("lead_score", 50),
            pain_point=data.get("pain_point"),
            service_interest=data.get("service_interest"),
            utm_source=data.get("utm_source"),
            utm_campaign=data.get("utm_campaign"),
            sent_to_meta=bool(data.get("conversion_sent_to_meta")),
        )
