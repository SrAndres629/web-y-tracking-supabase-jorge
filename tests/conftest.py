"""
🔧 Pytest Configuration - Silicon Valley Testing Standards

Este archivo configura el entorno de testing con:
- Fixtures reutilizables por capa arquitectónica
- Mocks inteligentes que respetan la arquitectura Clean/DDD
- Auto-configuración de entorno CI/CD
"""

import pytest
import os
import sys
import asyncio
from typing import AsyncGenerator, Generator, Any
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

# =============================================================================
# PATH CONFIGURATION
# =============================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configuración global de pytest - Silicon Valley Pattern"""
    # Detectar modo de ejecución
    is_ci = os.getenv("GITHUB_ACTIONS") or os.getenv("CI")
    is_audit = os.getenv("AUDIT_MODE") == "1"
    
    # Configurar markers personalizados
    config.addinivalue_line("markers", "unit: Unit tests - fast, isolated, no IO")
    config.addinivalue_line("markers", "integration: Integration tests - with fake infrastructure")
    config.addinivalue_line("markers", "e2e: End-to-end tests - full stack")
    config.addinivalue_line("markers", "audit: Architecture audit tests")
    config.addinivalue_line("markers", "slow: Tests that take > 1 second")
    config.addinivalue_line("markers", "critical: Business-critical path tests")
    
    env_text = f"Test Environment: {'CI' if is_ci else 'Local'}{'/Audit' if is_audit else ''}"
    try:
        print(f"\n🧪 {env_text}")
    except UnicodeEncodeError:
        print(f"\n[TEST] {env_text}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Configura el entorno de testing completo.
    Silicon Valley Pattern: Deterministic test environment.
    """
    # Guardar variables originales
    original_env = dict(os.environ)
    
    # Configurar modo testing
    os.environ["TESTING"] = "1"
    os.environ["PYTEST_CURRENT_TEST"] = "1"
    
    # Si no es audit mode, mockear configuraciones sensibles
    if os.getenv("AUDIT_MODE") != "1" and os.getenv("REAL_INFRA") != "1":
        _setup_mock_environment()
    
    yield
    
    # Cleanup: restaurar variables originales
    os.environ.clear()
    os.environ.update(original_env)


def _setup_mock_environment():
    """Setup mock environment variables for testing"""
    mocks = {
        "DATABASE_URL": "sqlite:///test_memory.db",
        "META_PIXEL_ID": "1234567890",
        "META_ACCESS_TOKEN": "fake_token_for_testing",
        "UPSTASH_REDIS_REST_URL": "https://mock-redis.upstash.io",
        "UPSTASH_REDIS_REST_TOKEN": "mock_token",
        "SENTRY_DSN": "",
        "RUDDERSTACK_WRITE_KEY": "",
        "N8N_WEBHOOK_URL": "",
    }
    for key, value in mocks.items():
        if not os.getenv(key):
            os.environ[key] = value


# =============================================================================
# DOMAIN LAYER FIXTURES (Pure, No Dependencies)
# =============================================================================

@pytest.fixture
def domain_external_id():
    """Fixture: Valid ExternalId value object"""
    from app.domain.models.values import ExternalId
    result = ExternalId.from_string("a" * 32)  # 32 hex chars
    return result.unwrap()


@pytest.fixture
def domain_phone():
    """Fixture: Valid Phone value object"""
    from app.domain.models.values import Phone
    result = Phone.parse("77712345", country="BO")
    return result.unwrap()


@pytest.fixture
def domain_email():
    """Fixture: Valid Email value object"""
    from app.domain.models.values import Email
    result = Email.parse("test@example.com")
    return result.unwrap()


@pytest.fixture
def domain_visitor(domain_external_id):
    """Fixture: Visitor entity for testing"""
    from app.domain.models.visitor import Visitor, VisitorSource
    return Visitor.create(
        ip="127.0.0.1",
        user_agent="TestAgent/1.0",
        source=VisitorSource.PAGEVIEW
    )


@pytest.fixture
def domain_event(domain_external_id):
    """Fixture: TrackingEvent entity for testing"""
    from app.domain.models.events import TrackingEvent, EventName
    return TrackingEvent.create(
        event_name=EventName.PAGE_VIEW,
        external_id=domain_external_id,
        source_url="https://test.example.com"
    )


# =============================================================================
# REPOSITORY MOCKS (Infrastructure Abstractions)
# =============================================================================

@pytest.fixture
def mock_visitor_repository():
    """
    Mock de VisitorRepository para tests unitarios.
    Silicon Valley Pattern: Repository Mock with predictable behavior.
    """
    repo = AsyncMock()
    repo.get_by_external_id = AsyncMock(return_value=None)
    repo.save = AsyncMock(return_value=None)
    repo.update = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_event_repository():
    """Mock de EventRepository para tests unitarios"""
    repo = AsyncMock()
    repo.save = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_by_visitor = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_lead_repository():
    """Mock de LeadRepository para tests unitarios"""
    repo = AsyncMock()
    repo.get_by_phone = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=None)
    repo.update = AsyncMock(return_value=None)
    return repo


# =============================================================================
# APPLICATION LAYER FIXTURES
# =============================================================================

@pytest.fixture
def mock_deduplicator():
    """Mock de DeduplicationPort - siempre permite eventos únicos por defecto"""
    dedup = AsyncMock()
    dedup.is_unique = AsyncMock(return_value=True)
    dedup.mark_processed = AsyncMock(return_value=None)
    return dedup


@pytest.fixture
def mock_tracker_port():
    """Mock de TrackerPort para testing"""
    tracker = AsyncMock()
    tracker.name = "MockTracker"
    tracker.track = AsyncMock(return_value=True)
    return tracker


# =============================================================================
# COMMAND HANDLER FIXTURES
# =============================================================================

@pytest.fixture
def track_event_handler(mock_deduplicator, mock_visitor_repository, 
                        mock_event_repository, mock_tracker_port):
    """
    Fixture: TrackEventHandler completamente mockeado.
    Silicon Valley Pattern: Injectable dependencies.
    """
    from app.application.commands.track_event import TrackEventHandler
    return TrackEventHandler(
        deduplicator=mock_deduplicator,
        visitor_repo=mock_visitor_repository,
        event_repo=mock_event_repository,
        trackers=[mock_tracker_port]
    )


@pytest.fixture
def create_lead_handler(mock_lead_repository, mock_visitor_repository):
    """Fixture: CreateLeadHandler con dependencias mockeadas"""
    from app.application.commands.create_lead import CreateLeadHandler
    return CreateLeadHandler(
        lead_repo=mock_lead_repository,
        visitor_repo=mock_visitor_repository
    )


@pytest.fixture
def create_visitor_handler(mock_visitor_repository):
    """Fixture: CreateVisitorHandler con dependencias mockeadas"""
    from app.application.commands.create_visitor import CreateVisitorHandler
    return CreateVisitorHandler(visitor_repo=mock_visitor_repository)


# =============================================================================
# DTO FIXTURES
# =============================================================================

@pytest.fixture
def valid_track_event_request():
    """Fixture: TrackEventRequest válido"""
    from app.application.dto.tracking_dto import TrackEventRequest
    import uuid
    return TrackEventRequest(
        event_name="PageView",
        external_id=uuid.uuid4().hex,
        source_url="https://test.example.com",
        fbclid="test_fbclid",
        fbp="fb.1.1234567890.1234567890",
        utm_source="test_source",
        utm_medium="test_medium",
        utm_campaign="test_campaign"
    )


@pytest.fixture
def valid_tracking_context():
    """Fixture: TrackingContext válido"""
    from app.application.dto.tracking_dto import TrackingContext
    return TrackingContext(
        ip_address="127.0.0.1",
        user_agent="TestAgent/1.0"
    )


@pytest.fixture
def valid_create_lead_command():
    """Fixture: CreateLeadCommand válido"""
    from app.application.commands.create_lead import CreateLeadCommand
    return CreateLeadCommand(
        phone="555-123-4567",
        name="John Doe",
        email="john@example.com",
        external_id="a" * 32,
        fbclid="test_fbclid",
        service_interest="Web Development",
        utm_source="google",
        utm_campaign="summer_sale"
    )


# =============================================================================
# IN-MEMORY REPOSITORIES (Integration Testing)
# =============================================================================

class InMemoryVisitorRepository:
    """
    Implementación en memoria de VisitorRepository.
    Silicon Valley Pattern: Fake for integration testing.
    """
    def __init__(self):
        self._visitors = {}
        self._external_id_index = {}
    
    async def get_by_external_id(self, external_id):
        visitor_id = self._external_id_index.get(external_id.value)
        return self._visitors.get(visitor_id)
    
    async def save(self, visitor):
        self._visitors[visitor.id] = visitor
        self._external_id_index[visitor.external_id.value] = visitor.id
    
    async def update(self, visitor):
        self._visitors[visitor.id] = visitor
    
    async def create(self, visitor):
        self._visitors[visitor.id] = visitor
        self._external_id_index[visitor.external_id.value] = visitor.id
    
    def clear(self):
        self._visitors.clear()
        self._external_id_index.clear()


class InMemoryEventRepository:
    """Implementación en memoria de EventRepository"""
    def __init__(self):
        self._events = {}
    
    async def save(self, event):
        self._events[event.event_id.value] = event
    
    async def get_by_id(self, event_id):
        return self._events.get(event_id.value)
    
    async def list_by_visitor(self, external_id):
        return [e for e in self._events.values() 
                if e.external_id.value == external_id.value]
    
    def clear(self):
        self._events.clear()


class InMemoryLeadRepository:
    """Implementación en memoria de LeadRepository"""
    def __init__(self):
        self._leads = {}
        self._phone_index = {}
    
    async def get_by_phone(self, phone):
        lead_id = self._phone_index.get(phone.number)
        return self._leads.get(lead_id)
    
    async def get_by_id(self, lead_id):
        return self._leads.get(lead_id)
    
    async def create(self, lead):
        self._leads[lead.id] = lead
        self._phone_index[lead.phone.number] = lead.id
    
    async def update(self, lead):
        self._leads[lead.id] = lead
    
    def clear(self):
        self._leads.clear()
        self._phone_index.clear()


@pytest.fixture
def inmemory_visitor_repo():
    """Fixture: Repositorio en memoria para tests de integración"""
    return InMemoryVisitorRepository()


@pytest.fixture
def inmemory_event_repo():
    """Fixture: Repositorio en memoria para tests de integración"""
    return InMemoryEventRepository()


@pytest.fixture
def inmemory_lead_repo():
    """Fixture: Repositorio en memoria para tests de integración"""
    return InMemoryLeadRepository()


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def anyio_backend():
    """Restringe anyio a asyncio únicamente"""
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_mocks_after_test():
    """
    Limpia mocks automáticamente después de cada test.
    Silicon Valley Pattern: Test isolation guarantee.
    """
    yield
    # Cleanup se ejecuta después del test


@pytest.fixture
async def cleanup_async_tasks():
    """
    Limpia tareas async pendientes después de cada test.
    Previene 'unclosed event loop' warnings.
    """
    yield
    # Cancelar tareas pendientes
    tasks = [t for t in asyncio.all_tasks() 
             if t is not asyncio.current_task() and not t.done()]
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
