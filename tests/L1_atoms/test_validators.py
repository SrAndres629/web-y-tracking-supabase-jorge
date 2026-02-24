import pytest
from app.core.validators import (
    validate_url,
    validate_email,
    validate_phone,
    PhoneValidationResult
)

# ===== URL Validation Tests =====

def test_validate_url_valid_https():
    """Test valid HTTPS URL."""
    is_valid, error = validate_url("https://example.com")
    assert is_valid is True
    assert error is None

def test_validate_url_valid_http():
    """Test valid HTTP URL."""
    is_valid, error = validate_url("http://example.com")
    assert is_valid is True
    assert error is None

def test_validate_url_invalid_scheme():
    """Test URL with unsupported scheme."""
    is_valid, error = validate_url("ftp://example.com")
    assert is_valid is False
    assert error == "Scheme must be one of: ['https', 'http']"

def test_validate_url_custom_schemes():
    """Test URL with custom allowed schemes."""
    is_valid, error = validate_url("ftp://example.com", allowed_schemes=["ftp"])
    assert is_valid is True
    assert error is None

    is_valid, error = validate_url("http://example.com", allowed_schemes=["ftp"])
    assert is_valid is False
    assert error == "Scheme must be one of: ['ftp']"

def test_validate_url_missing_scheme():
    """Test URL without scheme."""
    is_valid, error = validate_url("example.com")
    assert is_valid is False
    assert error == "Invalid URL format"

def test_validate_url_empty():
    """Test empty URL."""
    is_valid, error = validate_url("")
    assert is_valid is False
    assert error == "URL is required"

def test_validate_url_none():
    """Test None URL."""
    is_valid, error = validate_url(None)
    assert is_valid is False
    assert error == "URL is required"

def test_validate_url_mixed_case_scheme():
    """Test URL with mixed case scheme."""
    is_valid, error = validate_url("HTTPs://example.com")
    assert is_valid is True
    assert error is None

def test_validate_url_minimal_structure():
    """
    Test that the validator only checks for scheme existence and format '://'.
    It does not validate the host/path part in its current implementation.
    """
    is_valid, error = validate_url("http://")
    assert is_valid is True
    assert error is None


# ===== Email Validation Tests =====

def test_validate_email_valid():
    """Test valid email."""
    is_valid, normalized, error = validate_email("test@example.com")
    assert is_valid is True
    assert normalized == "test@example.com"
    assert error is None

def test_validate_email_normalization():
    """Test email normalization (lowercase, strip)."""
    is_valid, normalized, error = validate_email("  Test@Example.COM  ")
    assert is_valid is True
    assert normalized == "test@example.com"
    assert error is None

def test_validate_email_invalid():
    """Test invalid email format."""
    is_valid, normalized, error = validate_email("invalid-email")
    assert is_valid is False
    assert normalized is None
    assert error == "Invalid email format"

def test_validate_email_empty():
    """Test empty email."""
    is_valid, normalized, error = validate_email("")
    assert is_valid is False
    assert normalized is None
    assert error == "Email is required"


# ===== Phone Validation Tests =====

def test_validate_phone_valid_bo_mobile():
    """Test valid Bolivia mobile phone."""
    result = validate_phone("71234567", default_country="BO")
    assert result.is_valid is True
    assert result.normalized == "+59171234567"
    assert result.country_code == "BO"

def test_validate_phone_valid_bo_with_prefix():
    """Test valid Bolivia phone with 591 prefix."""
    result = validate_phone("59171234567", default_country="BO")
    assert result.is_valid is True
    assert result.normalized == "+59171234567"
    assert result.country_code == "BO"

def test_validate_phone_too_short():
    """Test phone too short."""
    result = validate_phone("123")
    assert result.is_valid is False
    assert result.error == "Phone too short"
