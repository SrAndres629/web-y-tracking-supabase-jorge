import uuid

import pytest

from app import database
from app.domain.models.values import Phone
from app.infrastructure.persistence.sql_lead_repo import SQLLeadRepository


@pytest.mark.asyncio
async def test_get_by_phone_returns_full_object():
    # 1. Setup DB
    database.init_tables()

    # 2. Insert a test lead
    test_phone = "+15550001234"
    test_name = "Health Check User"
    test_id = str(uuid.uuid4())

    # Clean up first to ensure clean state
    with database.get_cursor() as cur:
        cur.execute("DELETE FROM crm_leads WHERE whatsapp_phone = %s", (test_phone,))

    # Manual insert to ensure it works in SQLite with explicit ID
    with database.get_cursor() as cur:
        # Use simple query that matches the schema
        # id, whatsapp_phone, full_name, ...
        # If we use database.INSERT_LEAD_SQLITE it uses:
        # id, whatsapp_phone, meta_lead_id, fb_click_id, email, full_name
        cur.execute(
            "INSERT INTO crm_leads (id, whatsapp_phone, full_name, status) VALUES (%s, %s, %s, %s)",
            (test_id, test_phone, test_name, "new")
        )

    # 3. Test get_by_phone
    repo = SQLLeadRepository()
    phone_obj = Phone.parse(test_phone).unwrap()

    lead = await repo.get_by_phone(phone_obj)

    assert lead is not None
    assert str(lead.phone) == test_phone
    assert lead.name == test_name
    assert lead.id == test_id

    # Clean up
    with database.get_cursor() as cur:
        cur.execute("DELETE FROM crm_leads WHERE whatsapp_phone = %s", (test_phone,))


@pytest.mark.asyncio
async def test_get_by_id_returns_full_object():
    # 1. Setup DB
    # (init_tables handled by previous test or re-run)
    # But for safety in separate run:
    database.init_tables()

    # 2. Insert a test lead
    test_phone = "+15550005678"
    test_name = "ID Check User"
    test_id = str(uuid.uuid4())

    # Clean up
    with database.get_cursor() as cur:
        cur.execute("DELETE FROM crm_leads WHERE whatsapp_phone = %s", (test_phone,))

    with database.get_cursor() as cur:
        cur.execute(
            "INSERT INTO crm_leads (id, whatsapp_phone, full_name, status) VALUES (%s, %s, %s, %s)",
            (test_id, test_phone, test_name, "new")
        )

    # 3. Test get_by_id
    repo = SQLLeadRepository()

    lead = await repo.get_by_id(test_id)

    assert lead is not None
    assert str(lead.phone) == test_phone
    assert lead.name == test_name
    assert lead.id == test_id

    # Clean up
    with database.get_cursor() as cur:
        cur.execute("DELETE FROM crm_leads WHERE whatsapp_phone = %s", (test_phone,))
