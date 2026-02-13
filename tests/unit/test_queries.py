"""
🔍 Tests para Application Queries

Tests para los handlers de consultas (Query Handlers).
"""

import pytest
from unittest.mock import AsyncMock

from app.application.queries.get_visitor import GetVisitorQuery, GetVisitorHandler
from app.application.queries.list_visitors import ListVisitorsQuery, ListVisitorsHandler
from app.domain.models.visitor import Visitor, VisitorSource
from app.domain.models.values import ExternalId


class TestGetVisitorQuery:
    """Tests para GetVisitorHandler"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock configurado con los métodos necesarios"""
        repo = AsyncMock()
        repo.get_by_external_id = AsyncMock(return_value=None)
        return repo
    
    @pytest.fixture
    def handler(self, mock_repo):
        return GetVisitorHandler(visitor_repo=mock_repo)
    
    @pytest.mark.asyncio
    async def test_get_existing_visitor(self, handler, mock_repo):
        """Test: Obtener un visitante existente"""
        # Arrange
        external_id_val = "a" * 32
        external_id = ExternalId.from_string(external_id_val).unwrap()
        
        existing_visitor = Visitor.reconstruct(
            external_id=external_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            source=VisitorSource.PAGEVIEW
        )
        
        mock_repo.get_by_external_id = AsyncMock(return_value=existing_visitor)
        
        query = GetVisitorQuery(external_id=external_id_val)
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result.is_ok
        visitor_response = result.unwrap()
        assert visitor_response is not None
        assert visitor_response.external_id == external_id_val
        assert visitor_response.visit_count == 1
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_visitor(self, handler, mock_repo):
        """Test: Intentar obtener visitante inexistente retorna None (no error)"""
        mock_repo.get_by_external_id = AsyncMock(return_value=None)
        
        query = GetVisitorQuery(external_id="b" * 32)
        
        result = await handler.handle(query)
        
        assert result.is_ok
        assert result.unwrap() is None  # No encontrado = None, no error
    
    @pytest.mark.asyncio
    async def test_get_visitor_invalid_id(self, handler, mock_repo):
        """Test: ID de visitante inválido retorna error"""
        query = GetVisitorQuery(external_id="invalid-id")
        
        result = await handler.handle(query)
        
        assert result.is_err
        assert "Invalid external_id" in result.unwrap_err()
        mock_repo.get_by_external_id.assert_not_called()


class TestListVisitorsQuery:
    """Tests para ListVisitorsHandler"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock configurado con los métodos necesarios para listado"""
        repo = AsyncMock()
        repo.list_recent = AsyncMock(return_value=[])
        repo.count = AsyncMock(return_value=0)
        return repo
    
    @pytest.fixture
    def handler(self, mock_repo):
        return ListVisitorsHandler(visitor_repo=mock_repo)
    
    @pytest.mark.asyncio
    async def test_list_visitors_pagination(self, handler, mock_repo):
        """Test: Listar visitantes con paginación"""
        # Crear visitantes de prueba
        visitors = [
            Visitor.create(ip=f"192.168.1.{i}", user_agent="Test") 
            for i in range(5)
        ]
        
        mock_repo.list_recent = AsyncMock(return_value=visitors)
        mock_repo.count = AsyncMock(return_value=5)
        
        query = ListVisitorsQuery(limit=10, offset=0)
        result = await handler.handle(query)
        
        assert result.is_ok
        response = result.unwrap()
        assert len(response.items) == 5
        assert response.total == 5
        assert response.limit == 10
        assert response.offset == 0
    
    @pytest.mark.asyncio
    async def test_list_visitors_empty(self, handler, mock_repo):
        """Test: Listar cuando no hay visitantes"""
        mock_repo.list_recent = AsyncMock(return_value=[])
        mock_repo.count = AsyncMock(return_value=0)
        
        query = ListVisitorsQuery(limit=10, offset=0)
        result = await handler.handle(query)
        
        assert result.is_ok
        response = result.unwrap()
        assert len(response.items) == 0
        assert response.total == 0
    
    @pytest.mark.asyncio
    async def test_list_visitors_pagination_limits(self, handler, mock_repo):
        """Test: Límites de paginación se aplican correctamente"""
        mock_repo.list_recent = AsyncMock(return_value=[])
        mock_repo.count = AsyncMock(return_value=100)
        
        # Probar límite superior (máximo 100)
        query = ListVisitorsQuery(limit=200, offset=0)
        result = await handler.handle(query)
        
        assert result.is_ok
        response = result.unwrap()
        assert response.limit == 100  # Se limita a 100
        
        # Probar límite inferior (mínimo 1)
        query = ListVisitorsQuery(limit=0, offset=0)
        result = await handler.handle(query)
        
        assert result.is_ok
        response = result.unwrap()
        assert response.limit == 1  # Se ajusta a 1
    
    @pytest.mark.asyncio
    async def test_list_visitors_offset_handling(self, handler, mock_repo):
        """Test: Offset negativo se corrige a 0"""
        mock_repo.list_recent = AsyncMock(return_value=[])
        mock_repo.count = AsyncMock(return_value=10)
        
        query = ListVisitorsQuery(limit=10, offset=-5)
        result = await handler.handle(query)
        
        assert result.is_ok
        response = result.unwrap()
        assert response.offset == 0  # Se corrige a 0
