"""
👤 Tests para CreateVisitorHandler

Cobertura completa del comando de creación de visitantes.
"""

import pytest
from unittest.mock import AsyncMock

from app.application.commands.create_visitor import (
    CreateVisitorCommand, 
    CreateVisitorHandler
)
from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.models.values import ExternalId


class TestCreateVisitorHandler:
    """Suite de tests para CreateVisitorHandler"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock del repositorio de visitantes"""
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_repo):
        """Handler con repositorio mockeado"""
        return CreateVisitorHandler(visitor_repo=mock_repo)
    
    @pytest.mark.asyncio
    async def test_create_new_visitor_success(self, handler, mock_repo):
        """Test: Crear un visitante nuevo exitosamente"""
        # Arrange: No existe visitante previo
        mock_repo.get_by_external_id = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=None)
        
        command = CreateVisitorCommand(
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            fbclid="test_fbclid_123",
            fbp="fb.1.1234567890.9876543210",
            source="pageview",
            utm_source="facebook",
            utm_medium="cpc",
            utm_campaign="summer_sale"
        )
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.is_ok
        response = result.unwrap()
        assert response.fbclid == "test_fbclid_123"
        assert response.fbp == "fb.1.1234567890.9876543210"
        assert response.source == "pageview"
        assert response.visit_count == 1
        
        # Verificar que se llamó al repositorio
        mock_repo.create.assert_called_once()
        created_visitor = mock_repo.create.call_args[0][0]
        assert isinstance(created_visitor, Visitor)
        assert created_visitor.fbclid == "test_fbclid_123"
    
    @pytest.mark.asyncio
    async def test_returning_visitor_updates_count(self, handler, mock_repo):
        """Test: Visitante existente incrementa contador de visitas"""
        # Arrange: Existe un visitante previo
        existing_visitor = Visitor.create(
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
            source=VisitorSource.PAGEVIEW
        )
        # Simular una visita previa
        existing_visitor.record_visit()
        assert existing_visitor.visit_count == 2
        
        mock_repo.get_by_external_id = AsyncMock(return_value=existing_visitor)
        mock_repo.update = AsyncMock(return_value=None)
        
        command = CreateVisitorCommand(
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            fbclid="new_fbclid",  # Nuevo fbclid para actualizar
            source="pageview"
        )
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.is_ok
        response = result.unwrap()
        assert response.visit_count == 3  # Se incrementó una vez más
        
        # Verificar que se actualizó, no creó
        mock_repo.update.assert_called_once()
        mock_repo.create.assert_not_called()
        
        # Verificar que se actualizó el fbclid
        assert existing_visitor.fbclid == "new_fbclid"
    
    @pytest.mark.asyncio
    async def test_create_visitor_with_utm_data(self, handler, mock_repo):
        """Test: Crear visitante con datos UTM completos"""
        mock_repo.get_by_external_id = AsyncMock(return_value=None)
        
        command = CreateVisitorCommand(
            ip_address="10.0.0.1",
            user_agent="TestBot/1.0",
            source="facebook_ad",
            utm_source="google",
            utm_medium="organic",
            utm_campaign="spring_2024"
        )
        
        result = await handler.handle(command)
        
        assert result.is_ok
        mock_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_visitor_minimal_data(self, handler, mock_repo):
        """Test: Crear visitante con datos mínimos"""
        mock_repo.get_by_external_id = AsyncMock(return_value=None)
        
        command = CreateVisitorCommand(
            ip_address="127.0.0.1",
            user_agent="MinimalBot"
        )
        
        result = await handler.handle(command)
        
        assert result.is_ok
        response = result.unwrap()
        assert response.source == "pageview"  # Default value
        assert response.visit_count == 1
    
    @pytest.mark.asyncio
    async def test_handler_exception_handling(self, handler, mock_repo):
        """Test: Manejo de excepciones en el handler"""
        mock_repo.get_by_external_id = AsyncMock(
            side_effect=Exception("Database connection lost")
        )
        
        command = CreateVisitorCommand(
            ip_address="127.0.0.1",
            user_agent="TestBot"
        )
        
        result = await handler.handle(command)
        
        assert result.is_err
        error_msg = result.unwrap_err()
        assert "Database connection lost" in error_msg
