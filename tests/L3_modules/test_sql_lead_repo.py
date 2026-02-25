import pytest
import asyncio
from app import database
from app.infrastructure.persistence.repositories.lead_repository import LeadRepository as SQLLeadRepository
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Phone, Email, ExternalId

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 🛡️ Note: setup_db is now handled globally by conftest.py:clean_db and db_sqlite


@pytest.mark.asyncio
async def test_save_and_get_lead():
    repo = SQLLeadRepository()
    phone = Phone.parse("+59164714751").unwrap()
    lead = Lead.create(
        phone=phone,
        name="Test Lead",
        email=Email.parse("test@example.com").unwrap()
    )
    lead.qualify(pain_point="Tests", service_interest="QA")
    lead.score = 85

    await repo.save(lead)

    # Test get_by_id
    retrieved = await repo.get_by_id(lead.id)
    assert retrieved is not None
    assert retrieved.id == lead.id
    assert retrieved.name == "Test Lead"
    assert str(retrieved.phone) == "+59164714751"
    assert str(retrieved.email) == "test@example.com"
    assert retrieved.pain_point == "Tests"
    assert retrieved.service_interest == "QA"
    assert retrieved.score == 85

    # Test get_by_phone
    retrieved_by_phone = await repo.get_by_phone(phone)
    assert retrieved_by_phone is not None
    assert retrieved_by_phone.id == lead.id
    assert retrieved_by_phone.name == "Test Lead"

@pytest.mark.asyncio
async def test_get_by_external_id():
    repo = SQLLeadRepository()
    phone = Phone.parse("+59177777777").unwrap()
    ext_id = ExternalId.from_string("a" * 32).unwrap()
    lead = Lead.create(
        phone=phone,
        name="External Lead",
        external_id=ext_id
    )

    await repo.save(lead)

    retrieved = await repo.get_by_external_id(ext_id)
    assert retrieved is not None
    assert retrieved.id == lead.id
    assert retrieved.external_id == ext_id

@pytest.mark.asyncio
async def test_update_existing_lead():
    repo = SQLLeadRepository()
    phone = Phone.parse("+59160000000").unwrap()
    lead = Lead.create(phone=phone, name="Initial Name")
    await repo.save(lead)

    lead.name = "Updated Name"
    lead.update_status(LeadStatus.QUALIFIED)
    await repo.save(lead)

    retrieved = await repo.get_by_id(lead.id)
    assert retrieved.name == "Updated Name"
    assert retrieved.status == LeadStatus.QUALIFIED

@pytest.mark.asyncio
async def test_non_existent_lead():
    repo = SQLLeadRepository()
    assert await repo.get_by_id("non-existent") is None
    phone = Phone.parse("+59161111111").unwrap()
    assert await repo.get_by_phone(phone) is None
