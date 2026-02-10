import pytest
from unittest.mock import AsyncMock
from app.application.commands.create_visitor import CreateVisitorCommand, CreateVisitorHandler


class TestCreateVisitorHandler:
    @pytest.fixture
    def handler(self):
        return CreateVisitorHandler(visitor_repo=AsyncMock())
    
    @pytest.mark.asyncio
    async def test_create_new_visitor(self, handler):
        handler.visitor_repo.get_by_external_id = AsyncMock(return_value=None)
        command = CreateVisitorCommand(ip_address="1.2.3.4", user_agent="Mozilla")
        result = await handler.handle(command)
        assert result.is_ok
