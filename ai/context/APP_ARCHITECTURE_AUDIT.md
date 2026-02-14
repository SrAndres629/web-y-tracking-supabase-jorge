# 🔍 AUDITORÍA DE ARQUITECTURA - Carpeta app/

**Fecha**: 2026-02-10  
**Auditor**: Agente de IA  
**Estado**: ⚠️ **REQUIERE REFACTORIZACIÓN**

---

## 🎯 Resumen Ejecutivo

La carpeta `app/` presenta una **arquitectura híbrida** con código legacy mezclado con la nueva estructura Clean Architecture/DDD. Esto crea confusión para agentes de IA y viola los principios de separación de responsabilidades.

**Veredicto**: La estructura NO está completamente atomizada para edición eficiente con agentes de IA.

---

## 📊 Estadísticas Generales

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Total archivos Python** | 75 | - |
| **Total líneas de código** | 8,536 | - |
| **Promedio líneas/archivo** | 113.8 | ✅ Aceptable |
| **Archivos >300 líneas** | 5 | ❌ Problema |
| **Archivos 200-300 líneas** | 8 | ⚠️ Atención |
| **Archivos en raíz (anti-patrón)** | 13 | ❌ Problema grave |

---

## 🔴 Problemas Críticos Encontrados

### 1. **Código Legacy en Raíz** (13 archivos)

Archivos que violan la Clean Architecture al estar en la raíz de `app/`:

| Archivo | Líneas | Debería estar en | Problema |
|---------|--------|------------------|----------|
| `database.py` | 487 | `infrastructure/persistence/` | 🔴 Monolito de DB |
| `meta_capi.py` | 449 | `infrastructure/external/meta_capi/` | 🔴 Mezcla de responsabilidades |
| `tracking.py` | 413 | `application/` o `infrastructure/` | 🔴 Lógica de negocio dispersa |
| `cache.py` | 254 | `infrastructure/cache/` | 🟡 Duplicado con `infrastructure/cache/` |
| `sql_queries.py` | 212 | `infrastructure/persistence/` | 🟡 Queries sin abstracción |
| `models.py` | 108 | `domain/models/` o `infrastructure/` | 🟡 Duplicado con `domain/models/` |
| `services/__init__.py` | 267 | `application/services/` | 🟡 Servicios mal ubicados |

**Impacto en Agentes IA**: 
- Confusión sobre qué archivo usar (legacy vs nuevo)
- Imports impredecibles (`from app.tracking` vs `from app.application.commands.track_event`)
- Dificultad para determinar el "source of truth"

### 2. **Duplicación de Responsabilidades**

#### Tracking (4 implementaciones):
```
app/tracking.py                    (413 líneas) - LEGACY
app/application/commands/track_event.py    (nuevo)
app/interfaces/api/routes/tracking.py      (59 líneas) - nuevo
app/routes/tracking_routes.py      (324 líneas) - LEGACY
```

#### Cache (4 implementaciones):
```
app/cache.py                       (254 líneas) - LEGACY  
app/infrastructure/cache/redis_cache.py    (139 líneas) - nuevo
app/infrastructure/cache/memory_cache.py   (98 líneas) - nuevo
app/application/interfaces/cache_port.py   (87 líneas) - abstracción
```

#### Routes (2 sistemas):
```
app/routes/              (7 archivos, 1049 líneas) - LEGACY
app/interfaces/api/routes/  (3 archivos, 284 líneas) - nuevo
```

### 3. **Dependencias Problemáticas**

Los routes legacy importan directamente desde archivos de raíz:

```python
# app/routes/pages.py (legacy)
from app.database import get_visitor_fbclid, save_visitor      # ❌ Debería usar Repository
from app.tracking import generate_external_id, generate_fbc   # ❌ Debería usar Handler
from app.cache import cache_visitor_data                      # ❌ Debería usar Port

# app/routes/tracking_routes.py (legacy)
from app.meta_capi import send_elite_event                    # ❌ Acoplamiento directo
from app.tracking import send_n8n_webhook                     # ❌ Acoplamiento directo
from app.database import save_visitor                         # ❌ Bypass de abstracción
```

**Violaciones de Clean Architecture**:
- Interface layer → Infrastructure layer (salta Application)
- Acoplamiento directo a implementaciones concretas
- No se usan los Ports definidos en `application/interfaces/`

### 4. **Archivos Monolíticos**

Archivos que exceden el tamaño ideal para agentes de IA (<200 líneas):

| Archivo | Líneas | Responsabilidades | Riesgo |
|---------|--------|-------------------|--------|
| `database.py` | 487 | Conexión, queries, transacciones, utilidades | 🔴 Muy alto |
| `meta_capi.py` | 449 | API Meta, transformaciones, retry logic, event building | 🔴 Muy alto |
| `tracking.py` | 413 | Eventos, webhooks, identidad, cookies, tracking | 🔴 Muy alto |
| `routes/tracking_routes.py` | 324 | Endpoints, validación, lógica de negocio | 🔴 Alto |
| `core/decorators.py` | 301 | Múltiples decoradores no relacionados | 🟡 Medio |

---

## 🟡 Problemas Medios

### 5. **Estructura de Carpetas Inconsistente**

```
app/
├── application/          ✅ Correcto (Clean Architecture)
├── domain/              ✅ Correcto (Clean Architecture)
├── infrastructure/      ✅ Correcto (Clean Architecture)
├── interfaces/          ✅ Correcto (Clean Architecture)
├── middleware/          ⚠️ Debería estar en interfaces/api/
├── routes/              ❌ Duplicado con interfaces/api/routes/
├── services/            ⚠️ Debería estar en application/
└── [archivos sueltos]   ❌ Anti-patrón
```

### 6. **Configuración Dispersa**

- `app/config.py` (191 líneas) - Configuración legacy
- `app/infrastructure/config/settings.py` (256 líneas) - Configuración nueva

**Duplicación potencial** de variables de entorno y settings.

---

## ✅ Aspectos Positivos

### 1. **Nueva Arquitectura (Clean/DDD)**

Los archivos en la estructura correcta sí están bien atomizados:

```
app/application/commands/     ✅ 50-150 líneas promedio
app/application/queries/      ✅ 30-80 líneas
app/domain/models/           ✅ 20-100 líneas
app/infrastructure/cache/    ✅ 98-139 líneas
app/interfaces/api/routes/   ✅ 30-80 líneas
```

### 2. **Separación de Responsabilidades (en nueva arquitectura)**

| Capa | Archivos | Promedio Líneas | Estado |
|------|----------|-----------------|--------|
| Application | 16 | 64.5 | ✅ Bien |
| Domain | 11 | 110.9 | ⚠️ Aceptable |
| Infrastructure | 14 | 88.4 | ✅ Bien |
| Interfaces | 5 | 56.8 | ✅ Bien |

### 3. **Nuevos Routes Usan Arquitectura Correcta**

```python
# app/interfaces/api/routes/tracking.py (nuevo) ✅
from app.application.commands.track_event import TrackEventHandler
from app.application.dto.tracking_dto import TrackEventRequest
from app.interfaces.api.dependencies import get_track_event_handler
```

---

## 📋 Recomendaciones para Agentes de IA

### **NO editar estos archivos** (legacy, monolíticos):
- `app/database.py` - Usar `app/infrastructure/persistence/` en su lugar
- `app/tracking.py` - Usar `app/application/commands/tracking.py` en su lugar  
- `app/cache.py` - Usar `app/infrastructure/cache/` en su lugar
- `app/meta_capi.py` - Usar `app/infrastructure/external/meta_capi/` en su lugar
- `app/routes/*.py` - Usar `app/interfaces/api/routes/` en su lugar

### **SÍ editar estos archivos** (nueva arquitectura):
- `app/application/commands/*.py` - Comandos de negocio
- `app/application/queries/*.py` - Queries de lectura
- `app/domain/models/*.py` - Entidades y value objects
- `app/infrastructure/persistence/*.py` - Repositorios SQL
- `app/interfaces/api/routes/*.py` - Nuevos endpoints

---

## 🛠️ Plan de Refactorización Sugerido

### Fase 1: Consolidar Routes (1-2 días)
```bash
# Mover funcionalidad de app/routes/ a app/interfaces/api/routes/
app/routes/tracking_routes.py → app/interfaces/api/routes/tracking.py
app/routes/pages.py → app/interfaces/api/routes/pages.py
# etc.
```

### Fase 2: Migrar a Repositorios (2-3 días)
```python
# Antes (legacy)
from app.database import save_visitor

# Después (Clean Architecture)
from app.infrastructure.persistence.visitor_repo import PostgreSQLVisitorRepository
repo = PostgreSQLVisitorRepository()
repo.save(visitor)
```

### Fase 3: Extraer Módulos Monolíticos (3-5 días)
- `database.py` → `infrastructure/persistence/connection.py`, `unit_of_work.py`
- `tracking.py` → `application/tracking_service.py`, `infrastructure/tracking_client.py`
- `meta_capi.py` → `infrastructure/external/meta_capi/client.py`, `mapper.py`

### Fase 4: Unificar Configuración (1 día)
- Consolidar `app/config.py` y `app/infrastructure/config/settings.py`
- Eliminar duplicados

### Fase 5: Eliminar Código Legacy (1 día)
- Remover `app/routes/` (cuando todo esté migrado)
- Remover archivos sueltos de raíz

---

## 🎯 Métricas de Calidad Actuales

| Métrica | Valor Actual | Objetivo | Prioridad |
|---------|--------------|----------|-----------|
| Archivos en raíz | 13 | 0 | 🔴 Alta |
| Archivos >300 líneas | 5 | 0 | 🔴 Alta |
| Duplicación de funcionalidad | 4 áreas | 0 | 🔴 Alta |
| Imports legacy en nuevos routes | 0 | 0 | ✅ OK |
| Promedio líneas/archivo | 113.8 | <150 | ✅ OK |
| Cobertura Clean Architecture | 40% | 100% | 🟡 Media |

---

## 📝 Conclusión

**¿Está la carpeta app/ correctamente atomizada para análisis con agentes de IA?**

**Respuesta**: **PARCIALMENTE** ⚠️

- ✅ **La nueva arquitectura** (Clean/DDD en subcarpetas) SÍ está bien atomizada
- ❌ **El código legacy** (raíz de app/) NO está atomizado y confunde a los agentes
- ⚠️ **La coexistencia** de ambos sistemas crea ambigüedad

**Recomendación**: 
1. **Corto plazo**: Documentar claramente qué archivos son "safe to edit" para agentes
2. **Mediano plazo**: Completar la migración del código legacy a la nueva arquitectura
3. **Largo plazo**: Eliminar código legacy una vez validada la nueva arquitectura

**Para trabajo inmediato con agentes IA**: Usar únicamente archivos en:
- `app/application/commands/`
- `app/application/queries/`
- `app/domain/models/`
- `app/infrastructure/persistence/`
- `app/interfaces/api/routes/` (los nuevos, no `app/routes/`)

---

*Auditoría generada automáticamente*
