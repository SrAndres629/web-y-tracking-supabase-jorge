"""
📸 Snapshot Tests para DTOs

Verifica que los DTOs serializan exactamente como se espera.
Cualquier cambio en la estructura será detectado.
"""

import json
from datetime import datetime

from app.application.dto.lead_dto import LeadResponse
from app.application.dto.tracking_dto import TrackEventRequest, TrackEventResponse
from app.application.dto.visitor_dto import VisitorListResponse, VisitorResponse
from app.domain.models.values import ExternalId, Phone


class TestVisitorDtoSnapshots:
    """Snapshot tests para Visitor DTOs"""

    def test_visitor_response_snapshot(self):
        """
        Snapshot: VisitorResponse debe serializar consistentemente.
        """
        response = VisitorResponse(
            external_id="a" * 32,
            fbclid="test_fbclid_123",
            fbp="fb.1.1234567890.9876543210",
            source="pageview",
            visit_count=5,
            created_at=datetime(2026, 2, 10, 12, 0, 0),
            last_seen=datetime(2026, 2, 10, 14, 30, 0),
        )

        # Serializar a dict
        data = {
            "external_id": response.external_id,
            "fbclid": response.fbclid,
            "fbp": response.fbp,
            "source": response.source,
            "visit_count": response.visit_count,
            "created_at": response.created_at.isoformat() if response.created_at else None,
            "last_seen": response.last_seen.isoformat() if response.last_seen else None,
        }

        # Snapshot esperado
        expected = {
            "external_id": "a" * 32,
            "fbclid": "test_fbclid_123",
            "fbp": "fb.1.1234567890.9876543210",
            "source": "pageview",
            "visit_count": 5,
            "created_at": "2026-02-10T12:00:00",
            "last_seen": "2026-02-10T14:30:00",
        }

        assert data == expected, f"Snapshot mismatch: {json.dumps(data, indent=2)}"

    def test_visitor_list_response_snapshot(self):
        """
        Snapshot: VisitorListResponse con paginación.
        """
        visitors = [
            VisitorResponse(
                external_id=f"id_{i}",
                fbclid=None,
                fbp=None,
                source="pageview",
                visit_count=i,
                created_at=datetime(2026, 2, 10, 12, 0, 0),
                last_seen=datetime(2026, 2, 10, 14, 30, 0),
            )
            for i in range(3)
        ]

        response = VisitorListResponse(items=visitors, total=100, limit=10, offset=0)

        data = {
            "items": [
                {"external_id": v.external_id, "source": v.source, "visit_count": v.visit_count}
                for v in response.items
            ],
            "total": response.total,
            "limit": response.limit,
            "offset": response.offset,
        }

        expected = {
            "items": [
                {"external_id": "id_0", "source": "pageview", "visit_count": 0},
                {"external_id": "id_1", "source": "pageview", "visit_count": 1},
                {"external_id": "id_2", "source": "pageview", "visit_count": 2},
            ],
            "total": 100,
            "limit": 10,
            "offset": 0,
        }

        assert data == expected


class TestLeadDtoSnapshots:
    """Snapshot tests para Lead DTOs"""

    def test_lead_response_snapshot(self):
        """
        Snapshot: LeadResponse completo.
        """
        response = LeadResponse(
            id="lead-123-uuid",
            phone="+59177712345",
            name="John Doe",
            email="john@example.com",
            status="interested",
            score=75,
            service_interest="Web Development",
            created_at=datetime(2026, 2, 10, 10, 0, 0),
        )

        data = {
            "id": response.id,
            "phone": response.phone,
            "name": response.name,
            "email": response.email,
            "status": response.status,
            "score": response.score,
            "service_interest": response.service_interest,
            "created_at": response.created_at.isoformat() if response.created_at else None,
        }

        expected = {
            "id": "lead-123-uuid",
            "phone": "+59177712345",
            "name": "John Doe",
            "email": "john@example.com",
            "status": "interested",
            "score": 75,
            "service_interest": "Web Development",
            "created_at": "2026-02-10T10:00:00",
        }

        assert data == expected


class TestTrackingDtoSnapshots:
    """Snapshot tests para Tracking DTOs"""

    def test_track_event_request_snapshot(self):
        """
        Snapshot: TrackEventRequest con todos los campos.
        """
        request = TrackEventRequest(
            event_name="PageView",
            external_id="abc123abc123abc123abc123abc123ab",  # 32 chars
            source_url="https://example.com/page",
            fbclid="fbclidabc123",  # Sin underscore (sanitizado)
            fbp="fb.1.1234567890.9876543210",
            utm_source="facebook",
            utm_medium="cpc",
            utm_campaign="summer_sale",
            utm_term="web_development",
            utm_content="ad_variant_1",
            custom_data={"page_title": "Home", "scroll_depth": 75},
        )

        data = {
            "event_name": request.event_name,
            "external_id": request.external_id,
            "source_url": request.source_url,
            "fbclid": request.fbclid,
            "fbp": request.fbp,
            "custom_data": request.custom_data,
            "utm_source": request.utm_source,
            "utm_medium": request.utm_medium,
            "utm_campaign": request.utm_campaign,
            "utm_term": request.utm_term,
            "utm_content": request.utm_content,
            "custom_data": request.custom_data,
        }

        expected = {
            "event_name": "PageView",
            "external_id": "abc123abc123abc123abc123abc123ab",  # 32 chars
            "source_url": "https://example.com/page",
            "fbclid": "fbclidabc123",
            "fbp": "fb.1.1234567890.9876543210",
            "custom_data": {"page_title": "Home", "scroll_depth": 75},
            "utm_source": "facebook",
            "utm_medium": "cpc",
            "utm_campaign": "summer_sale",
            "utm_term": "web_development",
            "utm_content": "ad_variant_1",
        }

        assert data == expected

    def test_track_event_response_success_snapshot(self):
        """
        Snapshot: TrackEventResponse exitoso.
        """
        response = TrackEventResponse(
            success=True,
            event_id="evt_1234567890_abcdef",
            status="queued",
            message="PageView tracked successfully",
        )

        data = {
            "success": response.success,
            "event_id": response.event_id,
            "status": response.status,
            "message": response.message,
        }

        expected = {
            "success": True,
            "event_id": "evt_1234567890_abcdef",
            "status": "queued",
            "message": "PageView tracked successfully",
        }

        assert data == expected

    def test_track_event_response_error_snapshot(self):
        """
        Snapshot: TrackEventResponse con error.
        """
        response = TrackEventResponse(
            success=False, event_id=None, status="error", message="Invalid event name: UnknownEvent"
        )

        data = {
            "success": response.success,
            "event_id": response.event_id,
            "status": response.status,
            "message": response.message,
        }

        expected = {
            "success": False,
            "event_id": None,
            "status": "error",
            "message": "Invalid event name: UnknownEvent",
        }

        assert data == expected


# =============================================================================
# SNAPSHOTS DE ESTRUCTURAS DE DOMINIO
# =============================================================================


class TestDomainSnapshots:
    """Snapshot tests para estructuras de dominio"""

    def test_external_id_format_snapshot(self):
        """
        Snapshot: ExternalId siempre tiene formato específico.
        """
        external_id = ExternalId.from_request("192.168.1.1", "Mozilla/5.0")

        # Debe ser string hex de 32 caracteres
        assert len(external_id.value) == 32
        assert all(c in "0123456789abcdef" for c in external_id.value)

    def test_phone_normalization_snapshot(self):
        """
        Snapshot: Phone siempre normaliza a formato específico.
        """
        test_cases = [
            ("77712345", "+59177712345"),
            ("777-123-45", "+59177712345"),
            ("+591 777 12345", "+59177712345"),
        ]

        for input_num, expected in test_cases:
            result = Phone.parse(input_num, country="BO")
            assert result.is_ok
            assert result.unwrap().number == expected, f"Failed for {input_num}"

    def test_event_id_format_snapshot(self):
        """
        Snapshot: EventId siempre sigue formato evt_timestamp_entropy.
        """
        from app.domain.models.values import EventId

        event_id = EventId.generate()
        parts = event_id.value.split("_")

        assert len(parts) == 3
        assert parts[0] == "evt"
        assert parts[1].isdigit()  # timestamp
        assert len(parts[2]) >= 6  # entropy (6-8 chars)


# =============================================================================
# SNAPSHOTS DE COMPORTAMIENTO
# =============================================================================


class TestBehavioralSnapshots:
    """Snapshots de comportamiento específico"""

    def test_result_type_behavior_snapshot(self):
        """
        Snapshot: Result type tiene comportamiento específico.
        """
        ok_result = __import__("app.core.result", fromlist=["Result"]).Result.ok(42)
        err_result = __import__("app.core.result", fromlist=["Result"]).Result.err("error")

        # Comportamiento Ok
        assert ok_result.is_ok is True
        assert ok_result.is_err is False
        assert ok_result.unwrap() == 42
        assert ok_result.unwrap_or(0) == 42

        # Comportamiento Err
        assert err_result.is_ok is False
        assert err_result.is_err is True
        assert err_result.unwrap_err() == "error"
        assert err_result.unwrap_or(0) == 0

    def test_lead_scoring_behavior_snapshot(self):
        """
        Snapshot: Lead scoring tiene valores específicos por estado.
        """
        from app.domain.models.lead import Lead, LeadStatus

        phone = Phone.parse("77712345", country="BO").unwrap()
        lead = Lead.create(phone=phone)

        assert lead.score == 50  # Default

        lead.update_status(LeadStatus.BOOKED)
        assert lead.score == 70  # 50 + 20

        lead.update_status(LeadStatus.CLIENT_ACTIVE)
        assert lead.score == 100  # Máximo


# =============================================================================
# SNAPSHOT REGRESSION TESTS
# =============================================================================


class TestSnapshotRegressions:
    """Tests que detectan regresiones en outputs"""

    def test_no_unexpected_changes_in_dto_structure(self):
        """
        Verificar que la estructura de DTOs no cambia inesperadamente.

        Este test fallará si se agregan/quitan campos de los DTOs,
        forzando a actualizar el snapshot intencionalmente.
        """
        # Verificar que VisitorResponse tiene los campos esperados
        response = VisitorResponse(
            external_id="test",
            fbclid=None,
            fbp=None,
            source="pageview",
            visit_count=1,
            created_at=datetime.now(),
            last_seen=datetime.now(),
        )

        expected_fields = {
            "external_id",
            "fbclid",
            "fbp",
            "source",
            "visit_count",
            "created_at",
            "last_seen",
        }
        actual_fields = set(response.model_dump().keys())

        assert actual_fields == expected_fields, (
            f"DTO structure changed. Expected: {expected_fields}, Got: {actual_fields}"
        )
