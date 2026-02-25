import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.infrastructure.persistence.sql_lead_repo import SQLLeadRepository
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Phone, Email, ExternalId

@pytest.fixture
def mock_db_cursor():
    with patch("app.infrastructure.persistence.sql_lead_repo.database.get_cursor") as mock:
        yield mock

@pytest.mark.asyncio
async def test_get_by_phone_resolves_lead_correctly(mock_db_cursor):
    """
    Verifies that get_by_phone correctly maps a database row to a Lead object
    using the explicit column list.
    """
    # Arrange
    repo = SQLLeadRepository()
    phone_str = "+1234567890"
    phone = Phone.parse(phone_str).unwrap()
    valid_external_id = "a" * 32

    # Define the mock row based on the explicit column order:
    # 0: id, 1: whatsapp_phone, 2: full_name, 3: email, 4: meta_lead_id,
    # 5: fb_click_id, 6: fb_browser_id, 7: status, 8: lead_score,
    # 9: pain_point, 10: service_interest, 11: utm_source, 12: utm_campaign,
    # 13: created_at, 14: updated_at, 15: conversion_sent_to_meta

    mock_row = (
        "lead-uuid-123",        # 0: id
        phone_str,              # 1: whatsapp_phone
        "Test User",            # 2: full_name
        "test@example.com",     # 3: email
        "meta-lead-id-123",     # 4: meta_lead_id
        "fbclid-123",           # 5: fb_click_id
        valid_external_id,      # 6: fb_browser_id
        "interested",           # 7: status
        75,                     # 8: lead_score
        "Back pain",            # 9: pain_point
        "Physiotherapy",        # 10: service_interest
        "google",               # 11: utm_source
        "spring_sale",          # 12: utm_campaign
        "2023-01-01 10:00:00",  # 13: created_at
        "2023-01-02 10:00:00",  # 14: updated_at
        True                    # 15: conversion_sent_to_meta
    )

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row

    # Configure the context manager mock
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_cursor
    mock_db_cursor.return_value = mock_ctx

    # Act
    lead = await repo.get_by_phone(phone)

    # Assert
    assert lead is not None
    assert lead.id == "lead-uuid-123"
    assert str(lead.phone) == phone_str
    assert lead.name == "Test User"
    assert str(lead.email) == "test@example.com"
    assert lead.meta_lead_id == "meta-lead-id-123"
    assert lead.fbclid == "fbclid-123"
    assert str(lead.external_id) == valid_external_id
    assert lead.status == LeadStatus.INTERESTED
    assert lead.score == 75
    assert lead.pain_point == "Back pain"
    assert lead.service_interest == "Physiotherapy"
    assert lead.utm_source == "google"
    assert lead.utm_campaign == "spring_sale"
    # For dates, since we pass string and Lead doesn't validate runtime, we expect string back
    # or whatever we passed if fallback didn't trigger.
    assert lead.created_at == "2023-01-01 10:00:00"
    assert lead.updated_at == "2023-01-02 10:00:00"
    assert lead.sent_to_meta is True

    # Verify query used explicit columns
    args, _ = mock_cursor.execute.call_args
    query = args[0]
    assert "SELECT" in query
    assert "crm_leads" in query
    assert "whatsapp_phone" in query
    # Check that at least one of our specific columns is in the query to ensure we used the new list
    assert "fb_click_id" in query
    assert "fb_browser_id" in query
