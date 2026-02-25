import pytest
from app.core.validators import validate_phone, PhoneValidationResult


class TestPhoneValidator:
    """Test suite for validate_phone function."""

    @pytest.mark.parametrize(
        "phone_input, expected_normalized, expected_country",
        [
            # BO - Mobile (8 digits starting with 7/6/5)
            ("71234567", "+59171234567", "BO"),
            ("61234567", "+59161234567", "BO"),
            ("51234567", "+59151234567", "BO"),
            # BO - Landline (7 digits)
            ("2123456", "+5912123456", "BO"),
            # BO - Full format (591 + 7 digits)
            ("59171234567", "+59171234567", "BO"),
            # BO - Already normalized
            ("+59171234567", "+59171234567", "BO"),
            # US - Generic (1 + 10 digits)
            ("15551234567", "+15551234567", "US"),
            # Generic - Other (Assuming default country BO but doesn't match specific logic)
            ("5491112345678", "+5491112345678", "BO"),
            # Edge Cases - formatting characters
            ("(591) 712-34567", "+59171234567", "BO"),
            ("  71234567  ", "+59171234567", "BO"),
            ("712-345-67", "+59171234567", "BO"),
        ],
    )
    def test_validate_phone_valid_scenarios(
        self, phone_input, expected_normalized, expected_country
    ):
        """Test valid phone number scenarios."""
        result = validate_phone(phone_input)
        assert result.is_valid is True
        assert result.normalized == expected_normalized
        assert result.country_code == expected_country
        assert result.error is None

    @pytest.mark.parametrize(
        "phone_input, expected_error",
        [
            (None, "Phone is required"),
            ("", "Phone is required"),
            ("123", "Phone too short"),  # < 7 digits
            ("123456", "Phone too short"),  # 6 digits
            ("1234567890123456", "Phone too long"),  # > 15 digits
        ],
    )
    def test_validate_phone_invalid_scenarios(self, phone_input, expected_error):
        """Test invalid phone number scenarios."""
        result = validate_phone(phone_input)
        assert result.is_valid is False
        assert result.normalized is None
        assert result.error == expected_error

    def test_validate_phone_custom_default_country(self):
        """Test with a custom default country."""
        # Non-BO/US number should fallback to provided default country
        result = validate_phone("5491112345678", default_country="AR")
        assert result.is_valid is True
        assert result.normalized == "+5491112345678"
        assert result.country_code == "AR"

    def test_validate_phone_already_has_plus(self):
        """Test number that already starts with +."""
        result = validate_phone("+5491112345678")
        assert result.is_valid is True
        assert result.normalized == "+5491112345678"
        # Since it doesn't match BO/US specific logic, it falls back to default "BO"
        # unless we change default_country. The code logic for fallback is:
        # country_code=default_country
        assert result.country_code == "BO"
