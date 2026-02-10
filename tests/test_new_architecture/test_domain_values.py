import pytest
from app.domain.models.values import EventId, Phone, Email


class TestEventId:
    def test_generate_creates_valid_id(self):
        event_id = EventId.generate()
        assert event_id.value.startswith("evt_")
    
    def test_from_string_valid(self):
        result = EventId.from_string("evt_1234567890_abcdef")
        assert result.is_ok


class TestPhone:
    def test_parse_valid_bolivia(self):
        result = Phone.parse("77712345", country="BO")
        assert result.is_ok
        assert result.unwrap().number == "+59177712345"


class TestEmail:
    def test_parse_valid(self):
        result = Email.parse("Test@Example.COM")
        assert result.is_ok
        assert result.unwrap().address == "test@example.com"
