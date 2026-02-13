# 🧪 Testing Infrastructure - Silicon Valley Standards

## Overview

Este directorio contiene la suite de tests completa para el proyecto, siguiendo los estándares de testing de Silicon Valley:

- **Fast**: Tests unitarios < 10ms
- **Isolated**: Sin side effects entre tests  
- **Repeatable**: Mismo resultado siempre
- **Self-validating**: Boolean pass/fail
- **Timely**: Escritos junto al código

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures y configuración global
├── README.md                # Este archivo
├── unit/                    # Tests unitarios (puros, sin IO)
│   ├── test_create_lead_handler.py
│   ├── test_create_visitor_handler.py
│   ├── test_track_event_handler.py
│   ├── test_domain_lead.py
│   ├── test_queries.py
│   └── __init__.py
├── test_new_architecture/   # Tests de nueva arquitectura (transición)
│   ├── test_core_result.py
│   ├── test_domain_values.py
│   ├── test_domain_visitor.py
│   └── test_application_commands.py
├── 00_architecture/         # Tests de gobernanza arquitectónica
│   ├── test_boot_integrity.py
│   ├── test_no_legacy_paths.py
│   ├── test_serverless_packaging.py
│   └── test_template_integrity.py
├── 01_unit/                 # Tests legacy (por migrar)
├── 02_integration/          # Tests de integración
├── 03_audit/               # Tests de auditoría
└── 04_e2e/                 # Tests end-to-end
```

## Perfiles de Testing

### Quick (Desarrollo)
```bash
# Tests rápidos < 5 segundos
python scripts/test_runner.py quick
# o directamente:
pytest tests/unit tests/test_new_architecture -x
```

### Unit (Completo)
```bash
# Todos los tests unitarios
python scripts/test_runner.py unit
```

### Architecture (Gobernanza)
```bash
# Verifica reglas de arquitectura Clean/DDD
python scripts/test_runner.py architecture
```

### CI (Integración Continua)
```bash
# Suite completa con coverage
python scripts/test_runner.py ci
```

## Fixtures Disponibles

### Domain Fixtures
- `domain_external_id`: ExternalId válido
- `domain_phone`: Phone válido (Bolivia)
- `domain_email`: Email válido
- `domain_visitor`: Visitor entity
- `domain_event`: TrackingEvent entity

### Repository Mocks
- `mock_visitor_repository`: AsyncMock de VisitorRepository
- `mock_event_repository`: AsyncMock de EventRepository
- `mock_lead_repository`: AsyncMock de LeadRepository

### Handler Fixtures
- `track_event_handler`: TrackEventHandler mockeado
- `create_lead_handler`: CreateLeadHandler mockeado
- `create_visitor_handler`: CreateVisitorHandler mockeado

### In-Memory Repositories (Integration)
- `inmemory_visitor_repo`: Implementación en memoria
- `inmemory_event_repo`: Implementación en memoria
- `inmemory_lead_repo`: Implementación en memoria

## Ejemplos de Uso

### Test Unitario Básico
```python
import pytest

class TestMyFeature:
    @pytest.mark.asyncio
    async def test_feature_does_x(self, mock_visitor_repository):
        # Arrange
        mock_visitor_repository.get_by_external_id = AsyncMock(return_value=None)
        
        # Act
        result = await my_handler.handle(command)
        
        # Assert
        assert result.is_ok
```

### Test con In-Memory Repository
```python
@pytest.mark.asyncio
async def test_integration_create_visitor(inmemory_visitor_repo):
    handler = CreateVisitorHandler(visitor_repo=inmemory_visitor_repo)
    command = CreateVisitorCommand(ip_address="1.1.1.1", user_agent="Test")
    
    result = await handler.handle(command)
    
    assert result.is_ok
    # Verify persistence
    visitors = await inmemory_visitor_repo.list_recent(limit=10)
    assert len(visitors) == 1
```

## Reglas de Arquitectura Testeadas

### 1. No Legacy Imports
No se permite importar desde:
- `app.routes` (usar `app.interfaces.api.routes`)
- `app.templates` (usar `api/templates/`)

### 2. Clean Architecture Dependency Rule
- Domain NO importa de Application ni Infrastructure
- Application NO importa de Infrastructure

### 3. Domain Layer Purity
- Domain no tiene dependencias externas (FastAPI, SQL, etc.)

## Cobertura

```bash
# Generar reporte de cobertura
pytest tests/unit --cov=app --cov-report=html

# Ver cobertura en terminal
pytest tests/unit --cov=app --cov-report=term-missing
```

## Troubleshooting

### Tests fallan por encoding (Windows)
Los emojis en output pueden causar problemas en Windows. El conftest.py maneja esto automáticamente.

### Tests async fallan con "event loop closed"
Usar el fixture `cleanup_async_tasks` o marcar con `@pytest.mark.asyncio`.

### Import errors
Verificar que `sys.path` incluya el project root (hecho automáticamente en conftest.py).

## Métricas

- **Tests Unitarios**: 39
- **Tests Arquitectura**: 10
- **Tests Legacy**: ~122 (en migración)
- **Tiempo ejecución unit tests**: ~0.5s
- **Tiempo ejecución arquitectura**: ~8s

## Mantenimiento

Cuando agregues nuevos tests:
1. Ubicar en la carpeta correcta según la capa
2. Usar fixtures existentes cuando sea posible
3. Agregar fixtures reutilizables a `conftest.py`
4. Actualizar este README si agregas nuevas categorías
