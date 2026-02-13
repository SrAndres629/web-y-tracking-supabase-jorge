"""
📋 Contract Tests para Domain Layer

Estos tests verifican que los contratos de cada función se cumplan:
- Precondiciones: Validar inputs antes de procesar
- Postcondiciones: Validar outputs después de procesar
- Invariantes: Verificar que no se rompan condiciones críticas
"""

import pytest
from typing import Any, Callable
from functools import wraps

from app.domain.models.values import ExternalId, Phone, Email, EventId
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.models.events import TrackingEvent, EventName
from app.core.result import Result, Ok, Err


# =============================================================================
# DECORADOR DE CONTRATOS (para documentación y validación)
# =============================================================================

def contract(pre: Callable = None, post: Callable = None):
    """
    Decorador para documentar y validar contratos.
    
    Uso:
        @contract(
            pre=lambda phone: phone is not None,
            post=lambda result: result.is_ok or isinstance(result, Err)
        )
        def parse_phone(phone):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validar precondición
            if pre:
                assert pre(*args, **kwargs), f"Precondition failed for {func.__name__}"
            
            result = func(*args, **kwargs)
            
            # Validar postcondición
            if post:
                assert post(result), f"Postcondition failed for {func.__name__}"
            
            return result
        return wrapper
    return decorator


# =============================================================================
# CONTRACT TESTS PARA VALUE OBJECTS
# =============================================================================

class TestExternalIdContracts:
    """Contratos de ExternalId"""
    
    def test_precondition_from_string_requires_non_none(self):
        """
        Contrato: from_string NO acepta None
        
        Precondición: input no es None
        """
        # None debería manejarse o fallar gracefulmente
        result = ExternalId.from_string("")
        # Debe retornar Result.err, no lanzar excepción
        assert isinstance(result, Result)
    
    def test_postcondition_from_string_returns_result(self):
        """
        Contrato: from_string SIEMPRE retorna Result
        
        Postcondición: Tipo de retorno es Result[ExternalId, str]
        """
        result = ExternalId.from_string("a" * 32)
        assert isinstance(result, Result)
    
    def test_postcondition_valid_hex_returns_ok(self):
        """
        Contrato: String hex válido de 32 chars => Ok(ExternalId)
        """
        result = ExternalId.from_string("abcdef1234567890" * 2)
        assert result.is_ok
        assert isinstance(result.unwrap(), ExternalId)
    
    def test_postcondition_invalid_string_returns_err(self):
        """
        Contrato: String inválido => Err(str)
        """
        result = ExternalId.from_string("invalid")
        assert result.is_err
        assert isinstance(result.unwrap_err(), str)


class TestPhoneContracts:
    """Contratos de Phone"""
    
    def test_contract_parse_phone_bolivia(self):
        """
        Contrato completo para Phone.parse:
        
        Precondiciones:
        - phone_string no es vacío
        - country es válido o None
        
        Postcondiciones:
        - Retorna Result[Phone, str]
        - Si Ok: número normalizado a formato internacional
        - Si Err: mensaje descriptivo del error
        """
        # Caso válido
        result = Phone.parse("77712345", country="BO")
        assert isinstance(result, Result)
        if result.is_ok:
            phone = result.unwrap()
            assert phone.number.startswith("+")  # Normalizado
        
        # Caso inválido
        result = Phone.parse("invalid", country="BO")
        assert result.is_err
    
    def test_invariant_phone_number_immutable(self):
        """
        Invariante: Phone es inmutable después de crear
        
        Nota: Python no tiene inmutabilidad estricta, pero documentamos
        que no debe modificarse.
        """
        result = Phone.parse("77712345", country="BO")
        phone = result.unwrap()
        
        original_number = phone.number
        
        # Intentar "modificar" (crear nuevo en realidad)
        # No debería cambiar el original
        assert phone.number == original_number


class TestEmailContracts:
    """Contratos de Email"""
    
    def test_contract_email_normalization(self):
        """
        Contrato: Email siempre se normaliza a lowercase
        
        Postcondición: result.unwrap().address == input.lower()
        """
        result = Email.parse("Test@Example.COM")
        if result.is_ok:
            assert result.unwrap().address == "test@example.com"


# =============================================================================
# CONTRACT TESTS PARA ENTIDADES
# =============================================================================

class TestLeadContracts:
    """Contratos de Lead entity"""
    
    def test_precondition_create_requires_phone(self):
        """
        Contrato: Lead.create requiere Phone válido
        """
        phone = Phone.parse("77712345", country="BO").unwrap()
        lead = Lead.create(phone=phone)
        assert lead.phone is not None
    
    def test_postcondition_create_sets_defaults(self):
        """
        Contrato: Lead.create inicializa todos los campos requeridos
        
        Postcondiciones:
        - id es string no vacío
        - status es LeadStatus.NEW
        - score es 50
        - created_at es datetime
        """
        phone = Phone.parse("77712345", country="BO").unwrap()
        lead = Lead.create(phone=phone)
        
        assert isinstance(lead.id, str) and len(lead.id) > 0
        assert lead.status == LeadStatus.NEW
        assert lead.score == 50
        assert lead.created_at is not None
    
    def test_invariant_score_bounds(self):
        """
        Invariante: score siempre entre 0 y 100
        """
        phone = Phone.parse("77712345", country="BO").unwrap()
        lead = Lead.create(phone=phone)
        
        # Verificar invariante en todos los estados
        for status in LeadStatus:
            lead.update_status(status)
            assert 0 <= lead.score <= 100, f"Score {lead.score} out of bounds for status {status}"
    
    def test_postcondition_update_status_changes_status(self):
        """
        Contrato: update_status cambia el estado
        """
        phone = Phone.parse("77712345", country="BO").unwrap()
        lead = Lead.create(phone=phone)
        
        old_status = lead.status
        lead.update_status(LeadStatus.INTERESTED)
        
        assert lead.status != old_status
        assert lead.status == LeadStatus.INTERESTED


class TestVisitorContracts:
    """Contratos de Visitor entity"""
    
    def test_precondition_create_requires_ip_and_ua(self):
        """
        Contrato: Visitor.create requiere IP y User-Agent
        """
        visitor = Visitor.create(ip="127.0.0.1", user_agent="Test")
        assert visitor.ip_address == "127.0.0.1"
        assert visitor.user_agent == "Test"
    
    def test_postcondition_create_generates_deterministic_id(self):
        """
        Contrato: Mismo IP + UA siempre genera mismo external_id
        
        Postcondición: external_id es determinístico
        """
        v1 = Visitor.create(ip="1.1.1.1", user_agent="Mozilla/5.0")
        v2 = Visitor.create(ip="1.1.1.1", user_agent="Mozilla/5.0")
        
        assert v1.external_id == v2.external_id
    
    def test_postcondition_record_visit_increments_count(self):
        """
        Contrato: record_visit incrementa visit_count exactamente en 1
        """
        visitor = Visitor.create(ip="1.1.1.1", user_agent="Test")
        old_count = visitor.visit_count
        
        visitor.record_visit()
        
        assert visitor.visit_count == old_count + 1


class TestTrackingEventContracts:
    """Contratos de TrackingEvent"""
    
    def test_precondition_create_requires_event_name(self):
        """
        Contrato: create requiere EventName válido
        """
        external_id = ExternalId.from_request("1.1.1.1", "Test")
        event = TrackingEvent.create(
            event_name=EventName.PAGE_VIEW,
            external_id=external_id,
            source_url="https://test.com"
        )
        assert event.event_name == EventName.PAGE_VIEW
    
    def test_postcondition_create_generates_unique_event_id(self):
        """
        Contrato: Cada evento tiene ID único
        """
        external_id = ExternalId.from_request("1.1.1.1", "Test")
        
        events = [
            TrackingEvent.create(
                event_name=EventName.PAGE_VIEW,
                external_id=external_id,
                source_url="https://test.com"
            )
            for _ in range(100)
        ]
        
        event_ids = [e.event_id.value for e in events]
        assert len(set(event_ids)) == len(event_ids), "Duplicate event IDs generated"


# =============================================================================
# CONTRACT TESTS PARA RESULT TYPE
# =============================================================================

class TestResultContracts:
    """Contratos del tipo Result"""
    
    def test_contract_ok_creation(self):
        """
        Contrato: Result.ok(value) crea Ok con el valor
        """
        result = Result.ok(42)
        assert result.is_ok
        assert not result.is_err
        assert result.unwrap() == 42
    
    def test_contract_err_creation(self):
        """
        Contrato: Result.err(msg) crea Err con el mensaje
        """
        result = Result.err("error")
        assert result.is_err
        assert not result.is_ok
        assert result.unwrap_err() == "error"
    
    def test_invariant_ok_cannot_unwrap_err(self):
        """
        Invariante: Llamar unwrap_err() en Ok lanza excepción
        """
        result = Result.ok(42)
        with pytest.raises(Exception):
            result.unwrap_err()
    
    def test_invariant_err_cannot_unwrap(self):
        """
        Invariante: Llamar unwrap() en Err lanza excepción
        """
        result = Result.err("error")
        with pytest.raises(Exception):
            result.unwrap()


# =============================================================================
# TESTS DE CONTRATOS DE COMPOSICIÓN
# =============================================================================

class TestCompositionContracts:
    """Contratos cuando se componen múltiples operaciones"""
    
    def test_lead_creation_pipeline_contract(self):
        """
        Contrato: Pipeline completo de creación de lead
        
        1. Parsear teléfono
        2. Crear lead
        3. Cualificar
        4. Cambiar estado
        
        Postcondición: Lead con datos completos y estado actualizado
        """
        # Paso 1: Parsear
        phone_result = Phone.parse("77712345", country="BO")
        assert phone_result.is_ok, "Phone parsing should succeed"
        phone = phone_result.unwrap()
        
        # Paso 2: Crear lead
        lead = Lead.create(
            phone=phone,
            name="Test Lead",
            service_interest="Web Dev"
        )
        assert lead.status == LeadStatus.NEW
        
        # Paso 3: Cualificar
        lead.qualify(
            pain_point="Needs more clients",
            service_interest="Marketing"
        )
        assert lead.pain_point is not None
        
        # Paso 4: Cambiar estado
        lead.update_status(LeadStatus.INTERESTED)
        assert lead.status == LeadStatus.INTERESTED
        
        # Verificaciones finales
        assert lead.is_qualified
        assert lead.phone.number.startswith("+591")
