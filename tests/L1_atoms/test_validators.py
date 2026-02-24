"""
🧪 Tests para Validadores Core

Verifica la lógica de sanitización y validación de strings, emails y teléfonos.
"""

import pytest
from app.core.validators import sanitize_string, sanitize_utm, validate_email, validate_phone

@pytest.mark.L1
@pytest.mark.unit
class TestStringSanitization:
    """Tests para sanitize_string"""

    def test_sanitize_string_basic(self):
        """Sanitización básica: strip whitespace"""
        assert sanitize_string("  hello world  ") == "hello world"

    def test_sanitize_string_null_bytes(self):
        """
        🎯 Misión: Verificar remoción de Null Bytes (\x00)
        """
        assert sanitize_string("hello\x00world") == "helloworld"
        assert sanitize_string("\x00admin") == "admin"
        assert sanitize_string("system\x00") == "system"
        assert sanitize_string("\x00") is None

    def test_sanitize_string_control_characters(self):
        """Debe remover caracteres de control (< 32) excepto newline (\n)"""
        # \x01 (SOH), \x1f (US) deben ser removidos
        assert sanitize_string("hello\x01world\x1f") == "helloworld"

        # \r (Carriage Return) debe ser removido
        assert sanitize_string("line1\r\nline2") == "line1\nline2"

        # \n (Newline) debe ser mantenido
        assert sanitize_string("line1\nline2") == "line1\nline2"

        # \t (Tab, 9) debe ser removido según la lógica actual (ord < 32)
        assert sanitize_string("data1\tdata2") == "data1data2"

    def test_sanitize_string_truncation(self):
        """Debe truncar a max_length"""
        text = "abcdefghij"
        assert sanitize_string(text, max_length=5) == "abcde"
        assert sanitize_string(text, max_length=10) == "abcdefghij"
        assert sanitize_string(text, max_length=100) == "abcdefghij"

    def test_sanitize_string_empty_and_none(self):
        """Debe manejar None, strings vacíos o con solo espacios"""
        assert sanitize_string(None) is None
        assert sanitize_string("") is None
        assert sanitize_string("   ") is None
        assert sanitize_string("\x00\x01\x02") is None

    def test_sanitize_string_strip_after_cleaning(self):
        """Debe hacer strip después de remover caracteres prohibidos"""
        assert sanitize_string(" \x00 hello \x01 ") == "hello"

@pytest.mark.L1
@pytest.mark.unit
class TestUtmSanitization:
    """Tests para sanitize_utm"""

    def test_sanitize_utm_basic(self):
        assert sanitize_utm("facebook") == "facebook"
        assert sanitize_utm("google-cpc") == "google-cpc"
        assert sanitize_utm("summer_sale") == "summer_sale"

    def test_sanitize_utm_invalid_chars(self):
        # Solo permite alfanuméricos, guiones, guiones bajos y puntos
        assert sanitize_utm("facebook.com/ad") == "facebook.comad"
        assert sanitize_utm("utm@source") == "utmsource"
        assert sanitize_utm("hello world") == "helloworld"

    def test_sanitize_utm_truncation(self):
        long_utm = "a" * 150
        assert len(sanitize_utm(long_utm)) == 100

    def test_sanitize_utm_none_empty(self):
        assert sanitize_utm(None) is None
        assert sanitize_utm("") is None

@pytest.mark.L1
@pytest.mark.unit
class TestOtherValidators:
    """Tests rápidos para otros validadores core para mejorar cobertura"""

    def test_validate_email_basic(self):
        is_valid, normalized, error = validate_email("TEST@example.com ")
        assert is_valid is True
        assert normalized == "test@example.com"
        assert error is None

    def test_validate_email_invalid(self):
        is_valid, _, error = validate_email("invalid-email")
        assert is_valid is False
        assert error == "Invalid email format"

    def test_validate_phone_bo(self):
        # Bolivia mobile
        result = validate_phone("77712345")
        assert result.is_valid is True
        assert result.normalized == "+59177712345"
        assert result.country_code == "BO"

    def test_validate_phone_short(self):
        result = validate_phone("123")
        assert result.is_valid is False
        assert result.error == "Phone too short"
