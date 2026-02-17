"""
🎯 Create Lead Command.

Caso de uso: Convertir visitante (o anónimo) en lead.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.application.dto.lead_dto import LeadResponse
from app.core.result import Result
from app.domain.models.lead import Lead
from app.domain.models.values import ExternalId, Phone
from app.domain.repositories.lead_repo import LeadRepository
from app.domain.repositories.visitor_repo import VisitorRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateLeadCommand:
    """Input para crear lead."""

    phone: str
    name: str | None = None
    email: str | None = None
    external_id: str | None = None
    fbclid: str | None = None
    service_interest: str | None = None
    utm_source: str | None = None
    utm_campaign: str | None = None


class CreateLeadHandler:
    """Handler para crear leads."""

    def __init__(
        self,
        lead_repo: LeadRepository,
        visitor_repo: VisitorRepository | None = None,
    ):
        self.lead_repo = lead_repo
        self.visitor_repo = visitor_repo

    async def handle(self, cmd: CreateLeadCommand) -> Result[LeadResponse, str]:
        """
        Crea nuevo lead o actualiza existente.

        Lógica:
        1. Validar teléfono
        2. Verificar si ya existe (teléfono único)
        3. Si existe: actualizar info
        4. Si no existe: crear nuevo
        5. Link con visitor si se proporciona external_id
        """
        try:
            # 1. Validar teléfono
            phone_result = Phone.parse(cmd.phone)
            if phone_result.is_err:
                return Result.err(f"Invalid phone: {phone_result.unwrap_err()}")
            phone = phone_result.unwrap()

            # 2. Verificar existente
            existing = await self.lead_repo.get_by_phone(phone)
            if existing:
                logger.info("🔄 Lead already exists: %s", phone)
                # Actualizar info si se proporciona
                if cmd.name or cmd.email:
                    from app.domain.models.values import Email

                    email_result = Email.parse(cmd.email)
                    email = email_result.unwrap() if email_result.is_ok else None
                    existing.update_contact_info(name=cmd.name, email=email)
                    await self.lead_repo.update(existing)
                return Result.ok(self._to_response(existing))

            # 3. Buscar visitor si se proporciona external_id
            external_id = None
            if cmd.external_id and self.visitor_repo:
                ext_result = ExternalId.from_string(cmd.external_id)
                if ext_result.is_ok:
                    visitor = await self.visitor_repo.get_by_external_id(ext_result.unwrap())
                    if visitor:
                        external_id = visitor.external_id

            # 4. Parsear email si se proporciona
            email = None
            if cmd.email:
                from app.domain.models.values import Email

                email_result = Email.parse(cmd.email)
                if email_result.is_ok:
                    email = email_result.unwrap()

            # 5. Crear lead
            lead = Lead.create(
                phone=phone,
                name=cmd.name,
                email=email,
                external_id=external_id,
                fbclid=cmd.fbclid,
                service_interest=cmd.service_interest,
            )

            # Guardar UTMs
            lead.utm_source = cmd.utm_source
            lead.utm_campaign = cmd.utm_campaign

            await self.lead_repo.create(lead)
            logger.info("✅ New lead created: %s (%s)", lead.id, phone)

            return Result.ok(self._to_response(lead))

        except Exception as e:
            logger.exception("❌ Error creating lead: %s", str(e))
            return Result.err(str(e))

    def _to_response(self, lead: Lead) -> LeadResponse:
        return LeadResponse(
            id=lead.id,
            phone=str(lead.phone),
            name=lead.name,
            email=str(lead.email) if lead.email else None,
            status=lead.status.value,
            score=lead.score,
            service_interest=lead.service_interest,
            created_at=lead.created_at,
        )
