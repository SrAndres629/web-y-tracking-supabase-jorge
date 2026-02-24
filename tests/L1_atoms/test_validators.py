import pytest
from app.core.validators import validate_email

def test_validate_email_required():
    """Test that email is required (None or empty)."""
    is_valid, normalized, error = validate_email(None)
    assert is_valid is False
    assert normalized is None
    assert error == "Email is required"

    is_valid, normalized, error = validate_email("")
    assert is_valid is False
    assert normalized is None
    assert error == "Email is required"

def test_validate_email_normalization():
    """Test that email is normalized (lowercase and strip)."""
    is_valid, normalized, error = validate_email("  Test@Example.Com  ")
    assert is_valid is True
    assert normalized == "test@example.com"
    assert error is None

def test_validate_email_too_long():
    """Test that email length is validated."""
    # Email limit is 254 characters
    long_email = "a" * 245 + "@example.com" # 245 + 12 = 257 chars
    is_valid, normalized, error = validate_email(long_email)
    assert is_valid is False
    assert normalized is None
    assert error == "Email too long"

@pytest.mark.parametrize(
    "email",
    [
        "plainaddress",
        "@example.com",
        "Joe Smith <email@example.com>",
        "email.example.com",
        "email@example@example.com",
        "あいうえお@example.com",
        "email@example.com (Joe Smith)",
        "email@example",
    ],
)
def test_validate_email_invalid_format(email):
    """Test that invalid email formats are rejected by the current regex."""
    is_valid, normalized, error = validate_email(email)
    assert is_valid is False, f"Email {email} should be invalid"
    assert normalized is None
    assert error == "Invalid email format"


@pytest.mark.parametrize(
    "email",
    [
        "email@example.com",
        "firstname.lastname@example.com",
        "email@subdomain.example.com",
        "firstname+lastname@example.com",
        "1234567890@example.com",
        "email@example-one.com",
        "_______@example.com",
        "email@example.name",
        "email@example.museum",
        "email@example.co.jp",
        "firstname-lastname@example.com",
        ".email@example.com",  # Currently accepted
        "email.@example.com",  # Currently accepted
        "email..email@example.com",  # Currently accepted
    ],
)
def test_validate_email_success(email):
    """Test successful email validation."""
    is_valid, normalized, error = validate_email(email)
    assert is_valid is True, f"Email {email} should be valid"
    assert normalized == email.lower().strip()
    assert error is None
