# 🤖 AGENTS.md - Guía para Agentes de IA

## Arquitectura Clean/DDD - Jorge Aguirre Flores Web v3.0

---

## 📐 Visión General

Este proyecto usa **Clean Architecture** con **Domain-Driven Design (DDD)**.

```
┌─────────────────────────────────────────────────────────────┐
│                     🌐 Interface Layer                       │
│              (FastAPI Routes, Middleware, Webhooks)          │
├─────────────────────────────────────────────────────────────┤
│                   🎮 Application Layer                       │
│           (Commands, Queries, DTOs, Ports)                   │
├─────────────────────────────────────────────────────────────┤
│                     🧠 Domain Layer                          │
│         (Entities, Value Objects, Repository ABCs)           │
├─────────────────────────────────────────────────────────────┤
│                  🔧 Infrastructure Layer                     │
│    (DB Repositories, External APIs, Cache, Config)          │
├─────────────────────────────────────────────────────────────┤
│                      🔩 Core Layer                           │
│         (Result Types, Decorators, Validators - Pure)       │
└─────────────────────────────────────────────────────────────┘
```

**Regla de Dependencia:** Las capas superiores dependen de las inferiores, NUNCA al revés.

---

## 🗂️ Estructura de Carpetas

```
app/
├── core/                          # 🔩 Utilidades puras (sin dependencias)
│   ├── result.py                  # Result[T,E] type para manejo de errores
│   ├── decorators.py              # @retry, @circuit_breaker, @timed
│   └── validators.py              # Validación de teléfonos, emails, etc.
│
├── domain/                        # 🧠 Lógica de negocio pura
│   ├── models/                    # Entidades y Value Objects
│   │   ├── values.py              # EventId, ExternalId, Phone, Email
│   │   ├── visitor.py             # Entidad Visitor
│   │   ├── lead.py                # Entidad Lead
│   │   └── events.py              # Entidad TrackingEvent
│   ├── repositories/              # Interfaces (ABCs) de persistencia
│   │   ├── visitor_repo.py
│   │   ├── lead_repo.py
│   │   └── event_repo.py
│   └── exceptions.py              # Excepciones de dominio
│
├── application/                   # 🎮 Casos de uso (CQRS)
│   ├── commands/                  # Escrituras (TrackEvent, CreateLead)
│   │   ├── admin/                 # Comandos para el panel de administración
│   │   ├── identity/              # Comandos para la gestión de identidad (Google One Tap, WhatsApp)
│   │   ├── create_lead.py         # Original command
│   │   └── track_event.py         # Original command
│   ├── queries/                   # Lecturas (GetVisitor, ListLeads)
│   │   ├── admin/                 # Queries para el panel de administración
│   │   └── seo/                   # Queries para la gestión de SEO
│   ├── dto/                       # Data Transfer Objects
│   └── interfaces/                # Puertos (ports) para infraestructura
│       ├── cache_port.py
│       └── tracker_port.py
│
├── infrastructure/                # 🔧 Implementaciones concretas
│   ├── persistence/               # Repositorios SQL
│   │   ├── database.py            # Connection management
│   │   ├── visitor_repo.py
│   │   └── event_repo.py
│   ├── cache/                     # Redis/Memory cache
│   │   ├── redis_cache.py
│   │   └── memory_cache.py
│   ├── external/                  # APIs externas
│   │   ├── meta_capi/
│   │   └── rudderstack/
│   └── config/                    # Settings
│       └── settings.py
│
└── interfaces/                    # 🌐 Adaptadores de entrada
    └── api/
        ├── routes/                # Endpoints FastAPI
        │   ├── admin.py           # Nuevas rutas para el panel de administración
        │   ├── identity.py        # Nuevas rutas para la gestión de identidad
        │   ├── seo.py             # Nuevas rutas para SEO (sitemap, robots, metadata)
        │   ├── pages.py           # Rutas de páginas HTML (funcionalidades SEO migradas)
        │   └── tracking.py        # Rutas de tracking (existente)
        ├── middleware/            # Security, rate limiting
        └── dependencies.py        # FastAPI Depends factories
```

---

## 🎯 Patrones Clave

### 1. Result Type (Manejo de Errores)

```python
from app.core.result import Result, Ok, Err

async def find_visitor(id: str) -> Result[Visitor, str]:
    visitor = await repo.get(id)
    if visitor:
        return Result.ok(visitor)
    return Result.err("Visitor not found")

# Uso
result = await find_visitor("abc123")
if result.is_ok:
    visitor = result.unwrap()
else:
    error = result.unwrap_err()
```

### 2. CQRS (Command Query Responsibility Segregation)

**Commands** (modifican estado):
```python
# app/application/commands/track_event.py
@dataclass
class TrackEventCommand:
    request: TrackEventRequest
    context: TrackingContext

class TrackEventHandler:
    async def handle(self, cmd: TrackEventCommand) -> TrackEventResponse:
        # 1. Validar
        # 2. Ejecutar lógica de dominio
        # 3. Persistir
        # 4. Side effects (trackers)
        pass
```

**Queries** (solo lectura):
```python
# app/application/queries/get_visitor.py
@dataclass
class GetVisitorQuery:
    external_id: str

class GetVisitorHandler:
    async def handle(self, query: GetVisitorQuery) -> Result[VisitorResponse, str]:
        # Solo lectura, sin side effects
        pass
```

### 3. Repository Pattern

```python
# Domain: Contrato abstracto
class VisitorRepository(ABC):
    @abstractmethod
    async def get_by_external_id(self, id: ExternalId) -> Optional[Visitor]: ...

# Infrastructure: Implementación concreta
class PostgreSQLVisitorRepository(VisitorRepository):
    async def get_by_external_id(self, id: ExternalId) -> Optional[Visitor]:
        # SQL específico
        pass
```

### 4. Dependency Injection

```python
# app/interfaces/api/dependencies.py
def get_track_event_handler() -> TrackEventHandler:
    return TrackEventHandler(
        deduplicator=get_deduplicator(),
        visitor_repo=get_visitor_repository(),
        event_repo=get_event_repository(),
        trackers=get_trackers(),
    )

# Uso en routes
@router.post("/event")
async def track(
    handler: TrackEventHandler = Depends(get_track_event_handler)
):
    pass
```

---

## 🧪 Testing

### Unit Tests (dominio puro)
Los tests unitarios para los handlers (CommandHandlers y QueryHandlers) deben ser creados bajo `tests/unit/`.
```python
# Ejemplo de test unitario para un handler
from app.application.commands.track_event import TrackEventCommand, TrackEventHandler
# ... mocks de repositorios y puertos
async def test_track_event_handler_success(handler, mock_deduplicator, mock_visitor_repo, mock_event_repo):
    # ... test logic
    pass
```

### Integration Tests (con infraestructura fake)
```python
class InMemoryVisitorRepository(VisitorRepository):
    # Implementación en memoria para tests
    pass
```

---

## 📝 Convenciones de Código

### Nombres
- **Entidades:** Sustantivos (`Visitor`, `Lead`, `TrackingEvent`)
- **Value Objects:** Inmutables, con validación (`Phone`, `Email`, `EventId`)
- **Commands:** `VerboNounCommand` (`TrackEventCommand`)
- **Handlers:** `VerboNounHandler` (`TrackEventHandler`)
- **Repositories:** `NounRepository` (ABC), `PostgreSQLNounRepository` (impl)

### Imports
```python
# 1. Python stdlib
from typing import Optional

# 2. Third party
from pydantic import BaseModel

# 3. Application (de más interno a más externo)
from app.core.result import Result      # Core primero
from app.domain.models.visitor import Visitor  # Domain
from app.application.dto import TrackEventRequest  # Application
from app.infrastructure.cache import RedisCache  # Infrastructure
```

---

## 🔧 Cómo Agregar Features

### Ejemplo: Agregar nuevo tracker

1. **Crear implementación del port:**
```python
# app/infrastructure/external/new_tracker/tracker.py
class NewTracker(TrackerPort):
    @property
    def name(self) -> str:
        return "new_tracker"
    
    async def track(self, event: TrackingEvent, visitor: Visitor) -> bool:
        # Implementación
        pass
```

2. **Registrar en dependencies:**
```python
# app/interfaces/api/dependencies.py
def get_trackers() -> List[TrackerPort]:
    return [
        MetaTracker(),
        RudderStackTracker(),
        NewTracker(),  # Añadir aquí
    ]
```

### Ejemplo: Agregar nuevo comando

1. **Definir DTOs:**
```python
# app/application/dto/new_dto.py
class NewCommandRequest(BaseModel): ...
class NewCommandResponse(BaseModel): ...
```

2. **Implementar handler:**
```python
# app/application/commands/new_command.py
@dataclass
class NewCommand:
    data: NewCommandRequest

class NewCommandHandler:
    async def handle(self, cmd: NewCommand) -> Result[NewCommandResponse, str]:
        # Lógica
        pass
```

3. **Exponer en API:**
```python
# app/interfaces/api/routes/new_route.py
@router.post("/new")
async def new_endpoint(
    data: NewCommandRequest,
    handler: NewCommandHandler = Depends(get_new_handler)
):
    result = await handler.handle(NewCommand(data=data))
    return result.unwrap_or_error()
```

---

## 🚨 Anti-Patterns a Evitar

❌ **No hacer:**
- Importar `fastapi` en la capa de dominio
- Usar `dict` en lugar de Value Objects tipados
- Llamar a la DB directamente desde routes
- Lanzar excepciones genéricas (usar Result types)

✅ **Hacer:**
- Mantener domain puro (sin dependencias externas)
- Validar en los Value Objects
- Usar handlers para orquestar
- Retornar Result types para operaciones que pueden fallar

---

## 📚 Recursos

- **Clean Architecture** - Robert C. Martin
- **Domain-Driven Design** - Eric Evans
- **CQRS Pattern** - Martin Fowler
- **Repository Pattern** - Microsoft Docs

---

## 🆘 Troubleshooting

### Problema: Circular imports
**Solución:** Importar dentro de funciones o usar `TYPE_CHECKING`

### Problema: Tests lentos
**Solución:** Usar repositorios InMemory para unit tests

### Problema: Cambiar base de datos
**Solución:** Solo modificar `infrastructure/persistence/`, domain no cambia

---

## ✅ Checklist antes de commit

- [ ] Tests pasan (`pytest`)
- [ ] Type checking (`mypy`)
- [ ] No hay imports circulares
- [ ] Domain no depende de infrastructure
- [ ] Nuevos handlers tienen tests

---

*Documentación para Agentes de IA - Actualizada: 2026-02-10*
