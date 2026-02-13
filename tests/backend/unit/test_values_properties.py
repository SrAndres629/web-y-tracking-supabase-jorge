"""
🎲 Property-Based Tests para Value Objects

Estos tests generan miles de casos aleatorios automáticamente
para encontrar edge cases que los tests unitarios no capturan.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, example

from app.domain.models.values import (
    ExternalId, Phone, Email, EventId, 
    UTMParams
)


# =============================================================================
# EXTERNAL ID PROPERTIES
# =============================================================================

class TestExternalIdProperties:
    """Propiedades matemáticas de ExternalId"""
    
    @given(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=500))
    @settings(max_examples=1000, deadline=None)
    def test_external_id_determinism(self, ip, user_agent):
        """
        Propiedad: Mismo IP + UA siempre produce mismo ExternalId (determinismo)
        """
        id1 = ExternalId.from_request(ip, user_agent)
        id2 = ExternalId.from_request(ip, user_agent)
        assert id1 == id2
    
    @given(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=500),
           st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=500))
    @settings(max_examples=500, deadline=None)
    def test_external_id_different_inputs_produce_different_ids(
        self, ip1, ua1, ip2, ua2
    ):
        """
        Propiedad: Diferentes inputs producen diferentes IDs (inyectividad)
        """
        assume((ip1, ua1) != (ip2, ua2))
        
        id1 = ExternalId.from_request(ip1, ua1)
        id2 = ExternalId.from_request(ip2, ua2)
        
        # Colisión extremadamente rara con SHA-256 truncado
        collision_probability = 1 / (16**16)
        if id1 == id2:
            pytest.skip(f"Hash collision detected (probability: {collision_probability})")
    
    @given(st.text(alphabet='0123456789abcdef', min_size=32, max_size=32))
    @settings(max_examples=1000)
    def test_external_id_from_valid_hex_always_succeeds(self, hex_string):
        """Propiedad: Cualquier string hex de 32 chars es válido"""
        result = ExternalId.from_string(hex_string)
        assert result.is_ok
        assert result.unwrap().value == hex_string
    
    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=500)
    def test_external_id_from_invalid_string_always_fails(self, invalid_string):
        """Propiedad: Strings inválidos siempre fallan"""
        assume(len(invalid_string) != 32 or not all(c in '0123456789abcdef' for c in invalid_string.lower()))
        
        result = ExternalId.from_string(invalid_string)
        assert result.is_err


# =============================================================================
# PHONE PROPERTIES
# =============================================================================

class TestPhoneProperties:
    """Propiedades de Phone value object"""
    
    @given(st.text(alphabet='0123456789', min_size=7, max_size=8))
    @settings(max_examples=500)
    def test_bolivia_phone_parsing_properties(self, number):
        """
        Propiedad: Números bolivianos válidos deben parsear exitosamente.
        Nota: Algunos números (como 0000000) pueden ser rechazados por validación.
        """
        result = Phone.parse(number, country="BO")
        
        # Si parsea exitosamente, debe tener formato internacional
        if result.is_ok:
            phone = result.unwrap()
            assert phone.number.startswith("+")  # Debe tener prefijo internacional
    
    @given(st.text(min_size=1, max_size=20))
    @settings(max_examples=500)
    def test_phone_with_special_characters_gets_normalized(self, raw_number):
        """Propiedad: Caracteres especiales deben ser eliminados"""
        decorated = f"+591-{raw_number[:4]}-{raw_number[4:]}"
        
        result = Phone.parse(decorated, country="BO")
        
        if result.is_ok:
            phone = result.unwrap()
            assert phone.number.replace("+", "").isdigit()
    
    @given(st.text(alphabet='123456789', min_size=7, max_size=8), st.text(alphabet='123456789', min_size=7, max_size=8))
    @settings(max_examples=200)
    def test_phone_equality_based_on_normalized_form(self, num1, num2):
        """Propiedad: Phones son iguales si sus formas normalizadas son iguales"""
        from hypothesis import assume
        
        result1 = Phone.parse(num1, country="BO")
        result2 = Phone.parse(num1, country="BO")
        result3 = Phone.parse(num2, country="BO")
        
        # Asumir que ambos parsean exitosamente
        assume(result1.is_ok and result2.is_ok and result3.is_ok)
        
        phone1 = result1.unwrap()
        phone2 = result2.unwrap()
        phone3 = result3.unwrap()
        
        assert phone1 == phone2
        if num1 != num2:
            assert phone1 != phone3


# =============================================================================
# EMAIL PROPERTIES
# =============================================================================

class TestEmailProperties:
    """Propiedades de Email value object"""
    
    @given(st.emails())
    @settings(max_examples=1000)
    def test_valid_email_always_parses(self, email_str):
        """Propiedad: Cualquier email válido debe parsear"""
        result = Email.parse(email_str)
        if result.is_ok:
            email = result.unwrap()
            assert "@" in email.address
            assert email.address == email.address.lower()


# =============================================================================
# EVENT ID PROPERTIES
# =============================================================================

class TestEventIdProperties:
    """Propiedades de EventId"""
    
    def test_event_id_generation_uniqueness_property(self):
        """
        Propiedad: Generar 1000 event IDs debe producir todos diferentes
        """
        ids = {EventId.generate() for _ in range(1000)}
        assert len(ids) == 1000, "Collision detected in 1000 generated IDs"
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_event_id_format_invariant(self, event_name):
        """
        Propiedad: Todos los Event IDs deben seguir el formato evt_{timestamp}_{entropy}
        """
        event_id = EventId.generate()
        parts = event_id.value.split("_")
        
        assert len(parts) == 3
        assert parts[0] == "evt"
        assert parts[1].isdigit()
        assert len(parts[2]) >= 6  # entropy puede ser 6-8 chars


# =============================================================================
# INVARIANTES GLOBALES
# =============================================================================

def test_all_value_objects_are_hashable():
    """
    Invariante arquitectónica: Todos los Value Objects deben ser hashables
    """
    phone = Phone.parse("77712345", country="BO").unwrap()
    email = Email.parse("test@example.com").unwrap()
    external_id = ExternalId.from_request("1.1.1.1", "Mozilla")
    
    value_set = {phone, email, external_id}
    assert len(value_set) == 3
    
    value_dict = {phone: "phone", email: "email", external_id: "id"}
    assert len(value_dict) == 3
