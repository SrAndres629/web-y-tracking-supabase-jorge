"""
✅ L1 Atoms - Validators Tests

Tests for data validation logic (pure functions).
"""

import pytest

from app.core.validators import validate_phone

# =================================================================
# PHONE VALIDATION TESTS
# =================================================================

@pytest.mark.parametrize(
    "phone_input, expected_valid, expected_error",
    [
        (None, False, "Phone is required"),
        ("", False, "Phone is required"),
        ("123456", False, "Phone too short"),  # < 7 digits
        ("1" * 16, False, "Phone too long"),   # > 15 digits
    ],
)
def test_validate_phone_basic_errors(phone_input, expected_valid, expected_error):
    """Verifies basic error conditions for phone validation."""
    result = validate_phone(phone_input)
    assert result.is_valid == expected_valid
    assert result.error == expected_error
    if not expected_valid:
        assert result.normalized is None


@pytest.mark.parametrize(
    "phone_input, expected_normalized",
    [
        # --- Bolivia (Default) ---
        # 7 digits -> Add +591
        ("2234567", "+5912234567"),
        # 8 digits starting with 7 (Mobile) -> Add +591
        ("71234567", "+59171234567"),
        # 8 digits starting with 6 (Mobile) -> Add +591
        ("61234567", "+59161234567"),
        # 8 digits starting with 5 (Mobile?) -> Add +591
        ("51234567", "+59151234567"),
        # Starts with 591 and length 10 -> Keep as is (add +)
        ("5917123456", "+5917123456"),
        # Starts with +591 and length 10 (digits) -> Keep as is
        ("+5917123456", "+5917123456"),

        # --- Edge Cases for Bolivia Logic ---
        # 8 digits NOT starting with 7, 6, 5 -> Fallback (add +)
        ("21234567", "+21234567"),
        # Starts with 591 but length is NOT 10 (e.g. 11 digits) -> Fallback
        ("59112345678", "+59112345678"),

        # --- International (Generic) ---
        # US: Starts with 1, length 11 -> Add +
        ("15551234567", "+15551234567"),
        # US with + already
        ("+15551234567", "+15551234567"),

        # --- Fallback (Other countries/formats) ---
        ("44123456789", "+44123456789"), # UK example
    ],
)
def test_validate_phone_normalization(phone_input, expected_normalized):
    """Verifies normalization logic for various phone formats."""
    result = validate_phone(phone_input, default_country="BO")
    assert result.is_valid is True
    assert result.normalized == expected_normalized
    assert result.error is None


def test_validate_phone_custom_default_country():
    """Verifies behavior when default_country is NOT BO."""
    # Should skip BO logic and go to generic/fallback

    # 7 digits input with US default -> Fallback (add +)
    result = validate_phone("2234567", default_country="US")
    assert result.is_valid is True
    # BO logic would add +591, but here it should just add +
    assert result.normalized == "+2234567"
    assert result.country_code == "US"

    # US format explicitly handled
    result_us = validate_phone("15551234567", default_country="MX")
    assert result_us.is_valid is True
    assert result_us.normalized == "+15551234567"
    assert result_us.country_code == "US" # Should detect US code regardless of default


def test_validate_phone_with_formatting_chars():
    """Verifies that non-digit characters are stripped before validation."""
    # (712) 345-67 -> 71234567 (8 digits, starts with 7) -> +59171234567 (BO logic)
    result = validate_phone("(712) 345-67")
    assert result.is_valid is True
    assert result.normalized == "+59171234567"

    # +591 712 3456 -> 5917123456 (10 digits) -> +5917123456
    result = validate_phone("+591 712 3456")
    assert result.is_valid is True
    assert result.normalized == "+5917123456"
