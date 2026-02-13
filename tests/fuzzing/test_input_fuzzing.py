"""
🎯 Fuzzing Tests para Inputs

Tests que usan entradas aleatorias/maliciosas para encontrar
vulnerabilidades y comportamientos inesperados.
"""

import pytest
import random
import string
from hypothesis import given, strategies as st, settings

from app.domain.models.values import ExternalId, Phone, Email, EventId
from app.domain.models.lead import Lead
from app.domain.models.visitor import Visitor
from app.core.result import Result


# =============================================================================
# RANDOM INPUT FUZZING
# =============================================================================

class TestRandomInputFuzzing:
    """Fuzzing con entradas completamente aleatorias"""
    
    @given(st.binary(min_size=0, max_size=1000))
    @settings(max_examples=1000)
    def test_external_id_handles_binary_data(self, data):
        """
        Fuzzing: ExternalId debe manejar datos binarios sin crash.
        """
        try:
            # Intentar convertir bytes a string
            text = data.decode('utf-8', errors='ignore')
            result = ExternalId.from_string(text)
            # Debe retornar Result, no lanzar excepción
            assert isinstance(result, Result)
        except Exception as e:
            pytest.fail(f"ExternalId crashed on binary data: {e}")
    
    @given(st.text(alphabet=string.printable, min_size=0, max_size=100))
    @settings(max_examples=1000)
    def test_phone_handles_all_printable_chars(self, text):
        """
        Fuzzing: Phone.parse debe manejar cualquier string printable.
        """
        try:
            result = Phone.parse(text, country="BO")
            # Debe retornar Result, no lanzar excepción
            assert isinstance(result, Result)
        except Exception as e:
            pytest.fail(f"Phone crashed on input '{text}': {e}")
    
    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=1000)
    def test_email_handles_arbitrary_strings(self, text):
        """
        Fuzzing: Email.parse debe manejar cualquier string sin crash.
        """
        try:
            result = Email.parse(text)
            assert isinstance(result, Result)
        except Exception as e:
            pytest.fail(f"Email crashed on input '{text[:50]}...': {e}")


# =============================================================================
# MALICIOUS INPUT FUZZING
# =============================================================================

class TestMaliciousInputFuzzing:
    """Fuzzing con entradas maliciosas (inyección, XSS, etc.)"""
    
    MALICIOUS_STRINGS = [
        # SQL Injection
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "1; DELETE FROM users WHERE '1'='1",
        
        # XSS
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')",
        
        # Path Traversal
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        
        # Command Injection
        "; cat /etc/passwd",
        "| whoami",
        "`rm -rf /`",
        
        # Buffer Overflow attempts
        "A" * 10000,
        "A" * 100000,
        "A" * 1000000,
        
        # Null bytes
        "test\x00hidden",
        "\x00",
        
        # Unicode attacks
        "<script\u0000>",
        "<script\u0009>",
        "<script\u000C>",
        
        # Special chars
        "\"'\"'\"\"'\"'\"'\"\"'\"",
        "\\x00\\x00\\x00",
        "%00%00%00",
        
        # Emoji y caracteres especiales
        "🚀💻🔥" * 100,
        "👨‍👩‍👧‍👦" * 50,  # Family emoji (múltiple codepoints)
        
        # Control characters
        "".join(chr(i) for i in range(32)),  # All control chars
        "\n\r\t\x0b\x0c",
        
        # Very long strings
        "a" * 10000,
        "1" * 100000,
        
        # Mixed valid/invalid
        "+59177712345<script>",
        "test@example.com'; DROP TABLE users; --",
    ]
    
    @pytest.mark.parametrize("malicious_input", MALICIOUS_STRINGS)
    def test_phone_handles_malicious_input(self, malicious_input):
        """
        Security: Phone debe sanitizar o rechazar input malicioso.
        """
        result = Phone.parse(malicious_input, country="BO")
        
        # Debe retornar Result, no lanzar excepción
        assert isinstance(result, Result)
        
        # Si acepta, no debe contener código malicioso
        if result.is_ok:
            phone = result.unwrap()
            assert "<script>" not in phone.number
            assert "DROP TABLE" not in phone.number
    
    @pytest.mark.parametrize("malicious_input", MALICIOUS_STRINGS)
    def test_email_handles_malicious_input(self, malicious_input):
        """
        Security: Email debe sanitizar o rechazar input malicioso.
        """
        result = Email.parse(malicious_input)
        
        assert isinstance(result, Result)
        
        if result.is_ok:
            email = result.unwrap()
            assert "<script>" not in email.address
            assert "DROP TABLE" not in email.address
    
    @pytest.mark.parametrize("malicious_input", MALICIOUS_STRINGS)
    def test_external_id_handles_malicious_input(self, malicious_input):
        """
        Security: ExternalId debe manejar input malicioso.
        """
        result = ExternalId.from_string(malicious_input)
        
        assert isinstance(result, Result)
        # Input malicioso debería resultar en error, no crash


# =============================================================================
# BOUNDARY VALUE FUZZING
# =============================================================================

class TestBoundaryValueFuzzing:
    """Fuzzing en los límites de los valores"""
    
    BOUNDARY_CASES = [
        # Strings vacíos
        "",
        " ",
        "  ",
        "\t",
        "\n",
        
        # Límites de longitud
        "a",  # 1 char
        "a" * 31,  # Justo antes de 32
        "a" * 32,  # Exactamente 32
        "a" * 33,  # Justo después de 32
        "a" * 100,
        "a" * 1000,
        "a" * 10000,
        
        # Caracteres especiales en límites
        "0" * 32,  # Solo ceros
        "f" * 32,  # Solo f (hex válido)
        "g" * 32,  # Solo g (hex inválido)
    ]
    
    @pytest.mark.parametrize("boundary_input", BOUNDARY_CASES)
    def test_external_id_boundary_values(self, boundary_input):
        """
        Fuzzing: Probar límites de ExternalId.
        """
        result = ExternalId.from_string(boundary_input)
        assert isinstance(result, Result)
    
    def test_external_id_exact_32_hex(self):
        """
        Boundary: Exactamente 32 caracteres hex debe ser válido.
        """
        valid_32 = "abcdef1234567890" * 2  # 32 chars
        result = ExternalId.from_string(valid_32)
        assert result.is_ok
        assert result.unwrap().value == valid_32
    
    def test_external_id_31_chars_fails(self):
        """
        Boundary: 31 caracteres debe fallar.
        """
        invalid_31 = "a" * 31
        result = ExternalId.from_string(invalid_31)
        assert result.is_err
    
    def test_external_id_33_chars_fails(self):
        """
        Boundary: 33 caracteres debe fallar.
        """
        invalid_33 = "a" * 33
        result = ExternalId.from_string(invalid_33)
        assert result.is_err


# =============================================================================
# RESOURCE EXHAUSTION FUZZING
# =============================================================================

class TestResourceExhaustion:
    """Fuzzing para agotamiento de recursos"""
    
    @pytest.mark.slow
    def test_many_consecutive_parsings(self):
        """
        Stress: Muchos parseos consecutivos no deben agotar memoria.
        """
        for i in range(10000):
            result = Phone.parse(f"777{i:05d}", country="BO")
            assert isinstance(result, Result)
    
    @pytest.mark.slow
    def test_many_visitor_creations(self):
        """
        Stress: Muchas creaciones de visitantes.
        """
        visitors = []
        for i in range(1000):
            visitor = Visitor.create(
                ip=f"192.168.{i // 256}.{i % 256}",
                user_agent=f"Test/{i}"
            )
            visitors.append(visitor)
        
        assert len(visitors) == 1000
        # Todos deben tener IDs únicos
        ids = [v.external_id.value for v in visitors]
        assert len(set(ids)) == 1000


# =============================================================================
# ENCODING FUZZING
# =============================================================================

class TestEncodingFuzzing:
    """Fuzzing con diferentes encodings"""
    
    ENCODING_TEST_CASES = [
        # UTF-8 edge cases
        "\u0000",  # Null
        "\uFFFF",  # Max BMP
        "\U0010FFFF",  # Max Unicode
        
        # Surrogate pairs (si se escapan mal)
        "\ud83d\ude80",  # Rocket emoji
        
        # Right-to-left
        "مرحبا",  # Árabe
        "שלום",  # Hebreo
        
        # CJK
        "こんにちは",  # Japonés
        "你好",  # Chino
        "안녕하세요",  # Coreano
        
        # Emoji
        "👨‍💻",  # Persona en computadora
        "🏳️‍🌈",  # Bandera arcoíris
        "👨‍👩‍👧‍👦",  # Familia
        
        # Zalgo text
        "Z̴͓͓͓a̴͓͓͓l̴͓͓͓g̴͓͓͓o̴͓͓͓",
        
        # RTL override
        "‮lrive‭",
        
        # Zero-width chars
        "test\u200btest",  # Zero-width space
        "test\u200ctest",  # Zero-width non-joiner
        "test\u200dtest",  # Zero-width joiner
        "test\ufefftest",  # BOM
    ]
    
    @pytest.mark.parametrize("encoding_input", ENCODING_TEST_CASES)
    def test_phone_handles_unicode(self, encoding_input):
        """
        Fuzzing: Phone debe manejar Unicode correctamente.
        """
        try:
            result = Phone.parse(encoding_input, country="BO")
            assert isinstance(result, Result)
        except UnicodeError as e:
            # UnicodeError es aceptable, pero no otras excepciones
            pass
    
    @pytest.mark.parametrize("encoding_input", ENCODING_TEST_CASES)
    def test_email_handles_unicode(self, encoding_input):
        """
        Fuzzing: Email debe manejar Unicode correctamente.
        """
        try:
            result = Email.parse(encoding_input)
            assert isinstance(result, Result)
        except UnicodeError:
            pass


# =============================================================================
# RANDOMIZED STRESS TESTS
# =============================================================================

class TestRandomizedStress:
    """Tests de estrés con aleatoriedad"""
    
    def test_random_external_id_generation(self):
        """
        Fuzzing: Generar ExternalIds con inputs aleatorios.
        """
        for _ in range(1000):
            # IP aleatoria
            ip = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            
            # User-Agent aleatorio
            ua_length = random.randint(1, 500)
            ua = ''.join(random.choices(string.ascii_letters + string.digits + " -_/.,()", k=ua_length))
            
            # Debe generar sin crash
            external_id = ExternalId.from_request(ip, ua)
            assert isinstance(external_id, ExternalId)
            assert len(external_id.value) == 32
    
    def test_random_lead_creation(self):
        """
        Fuzzing: Crear leads con datos aleatorios.
        """
        for _ in range(100):
            # Teléfono aleatorio boliviano
            number = f"777{random.randint(10000, 99999)}"
            result = Phone.parse(number, country="BO")
            
            if result.is_ok:
                phone = result.unwrap()
                
                # Nombre aleatorio
                name_length = random.randint(1, 100)
                name = ''.join(random.choices(string.ascii_letters + " ", k=name_length))
                
                # Crear lead
                lead = Lead.create(phone=phone, name=name.strip())
                assert lead.phone == phone
                assert isinstance(lead.id, str)


# =============================================================================
# CRASH DETECTION
# =============================================================================

def test_no_crash_on_none_input():
    """
    Fuzzing: None input no debe causar crash.
    """
    try:
        # Estos pueden fallar, pero no deben hacer crash
        Phone.parse(None, country="BO")  # type: ignore
        pytest.fail("Should have raised TypeError")
    except (TypeError, AttributeError):
        pass  # Expected
    
    try:
        Email.parse(None)  # type: ignore
        pytest.fail("Should have raised TypeError")
    except (TypeError, AttributeError):
        pass


def test_no_crash_on_int_input():
    """
    Fuzzing: Input tipo int no debe causar crash.
    """
    try:
        result = Phone.parse(12345, country="BO")  # type: ignore
        assert isinstance(result, Result)
    except (TypeError, AttributeError):
        pass
