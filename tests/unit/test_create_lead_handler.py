import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.commands.create_lead import CreateLeadHandler, CreateLeadCommand
from app.core.result import Result
from app.domain.models.lead import Lead, LeadStatus
from app.domain.models.values import Phone, ExternalId, Email
from app.domain.models.visitor import Visitor, VisitorSource

@pytest.fixture
def mock_lead_repo():
    return AsyncMock()

@pytest.fixture
def mock_visitor_repo():
    return AsyncMock()

@pytest.fixture
def handler(mock_lead_repo, mock_visitor_repo):
    return CreateLeadHandler(
        lead_repo=mock_lead_repo,
        visitor_repo=mock_visitor_repo,
    )

@pytest.fixture
def base_command():
    return CreateLeadCommand(
        phone="555-123-4567",
        name="John Doe",
        email="john.doe@example.com",
        external_id="visitor-123",
        fbclid="fb-clid-abc",
        service_interest="Web Development",
        utm_source="google",
        utm_campaign="summer_sale",
    )

@pytest.mark.asyncio
async def test_handle_invalid_phone(handler, base_command):
    base_command.phone = "invalid-phone"
    result = await handler.handle(base_command)
    
    assert result.is_err
    assert "Invalid phone" in result.unwrap_err()

@pytest.mark.asyncio
async def test_handle_existing_lead_updates_info(handler, mock_lead_repo, base_command):
    existing_lead = Lead.create(phone=Phone.parse("555-123-4567").unwrap(), name="Old Name")
    mock_lead_repo.get_by_phone.return_value = existing_lead
    
    cmd = CreateLeadCommand(
        phone="555-123-4567",
        name="New Name",
        email="new.email@example.com",
    )
    result = await handler.handle(cmd)
    
    assert result.is_ok
    mock_lead_repo.get_by_phone.assert_called_once_with(Phone.parse("555-123-4567").unwrap())
    mock_lead_repo.update.assert_called_once_with(existing_lead)
    assert existing_lead.name == "New Name"
    assert existing_lead.email == Email.parse("new.email@example.com").unwrap()

@pytest.mark.asyncio
async def test_handle_existing_lead_no_new_info(handler, mock_lead_repo, base_command):
    existing_lead = Lead.create(phone=Phone.parse("555-123-4567").unwrap(), name="Old Name")
    mock_lead_repo.get_by_phone.return_value = existing_lead
    
    cmd = CreateLeadCommand(phone="555-123-4567") # No name or email provided
    result = await handler.handle(cmd)
    
    assert result.is_ok
    mock_lead_repo.get_by_phone.assert_called_once()
    mock_lead_repo.update.assert_not_called() # Should not update if no new info

@pytest.mark.asyncio
async def test_handle_new_lead_created_without_external_id(handler, mock_lead_repo, mock_visitor_repo, base_command):
    mock_lead_repo.get_by_phone.return_value = None # No existing lead
    mock_visitor_repo.get_by_external_id.return_value = None # No visitor
    
    cmd = CreateLeadCommand(
        phone="555-987-6543",
        name="Jane Doe",
        email="jane.doe@example.com",
        service_interest="SEO",
        utm_source="facebook",
    )
    result = await handler.handle(cmd)
    
    assert result.is_ok
    mock_lead_repo.create.assert_called_once()
    created_lead = mock_lead_repo.create.call_args[0][0]
    assert created_lead.phone == Phone.parse("555-987-6543").unwrap()
    assert created_lead.name == "Jane Doe"
    assert created_lead.email == Email.parse("jane.doe@example.com").unwrap()
    assert created_lead.service_interest == "SEO"
    assert created_lead.utm_source == "facebook"
    assert created_lead.external_id is None # No external_id linked
    mock_visitor_repo.get_by_external_id.assert_not_called() # visitor_repo not used if external_id is None in cmd

@pytest.mark.asyncio
async def test_handle_new_lead_created_with_matching_visitor(handler, mock_lead_repo, mock_visitor_repo, base_command):
    mock_lead_repo.get_by_phone.return_value = None # No existing lead
    
    # Mock an existing visitor
    mock_visitor = Visitor.create(ip="1.1.1.1", user_agent="test", source=VisitorSource.DIRECT)
    mock_visitor._external_id = ExternalId("visitor-123") # Manually set for mock
    mock_visitor_repo.get_by_external_id.return_value = mock_visitor
    
    cmd = CreateLeadCommand(
        phone="555-999-0000",
        name="Alice",
        external_id="visitor-123",
    )
    result = await handler.handle(cmd)
    
    assert result.is_ok
    mock_lead_repo.create.assert_called_once()
    created_lead = mock_lead_repo.create.call_args[0][0]
    assert created_lead.external_id == ExternalId("visitor-123")
    mock_visitor_repo.get_by_external_id.assert_called_once_with(ExternalId("visitor-123"))

@pytest.mark.asyncio
async def test_handle_new_lead_created_with_external_id_no_matching_visitor(handler, mock_lead_repo, mock_visitor_repo, base_command):
    mock_lead_repo.get_by_phone.return_value = None # No existing lead
    mock_visitor_repo.get_by_external_id.return_value = None # No matching visitor
    
    cmd = CreateLeadCommand(
        phone="555-111-2222",
        name="Bob",
        external_id="visitor-456",
    )
    result = await handler.handle(cmd)
    
    assert result.is_ok
    mock_lead_repo.create.assert_called_once()
    created_lead = mock_lead_repo.create.call_args[0][0]
    assert created_lead.external_id is None # No external_id linked as no visitor found
    mock_visitor_repo.get_by_external_id.assert_called_once_with(ExternalId("visitor-456"))

@pytest.mark.asyncio
async def test_handle_exception_during_processing(handler, mock_lead_repo, base_command):
    mock_lead_repo.get_by_phone.side_effect = Exception("DB error")
    result = await handler.handle(base_command)
    
    assert result.is_err
    assert "DB error" in result.unwrap_err()
