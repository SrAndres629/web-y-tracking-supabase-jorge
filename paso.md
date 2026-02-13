# PASO.md - Playbook Maestro de Refactorizacion + Reparacion Continua

Fecha: 2026-02-11  
Proyecto: Jorge Aguirre Flores Web v3.0  
Objetivo: cerrar la migracion Clean/DDD sin romper produccion, con ciclos rapidos de deteccion/correccion.

---

## 0) Contexto real actual (baseline tecnico)

### Estado de avance consolidado
- Arquitectura en transicion avanzada: capa `application` ya desacoplada de imports legacy directos.
- Rutas `interfaces/api/routes/**` ya no importan legacy directo; ahora consumen `LegacyFacade`.
- Source of truth de templates alineado: `api/templates/**`.
- Serverless packaging corregido: `vercel.json` con include de `api/templates/**` + `static/**`.
- Guard-rails de arquitectura activos con tests.

### Deuda legacy aun activa (inventario de riesgo)
Persisten acoples directos a legacy en:
- `app/tracking.py` -> `app.cache`
- `app/meta_capi.py` -> `app.tracking`, `app.cache`
- `app/services/__init__.py` -> `app.database`, `app.cache`
- `app/maintenance.py` -> `app.database`
- `app/diagnostics.py` -> `app.database`
- `app/retry_queue.py` -> `app.meta_capi`
- `app/interfaces/api/dependencies.py` -> `app.database`, `app.meta_capi` (centralizado/transicional)

Interpretacion:
- La deuda ya esta encapsulada, pero aun existe.
- El cierre exitoso requiere remover dependencia interna legacy->legacy y mover contratos a puertos/repos.

---

## 1) Principios operativos "Silicon Valley + PhD rigor"

1. Refactor en slices pequenos, reversibles, medibles.
2. Cada cambio estructural tiene test de comportamiento + test de arquitectura.
3. No merge sin evidencia: comando ejecutado + resultado + impacto esperado.
4. Cuando algo se rompe: rollback logico (feature flag/facade fallback), no improvisacion.
5. La velocidad la da la calidad de observabilidad, no la cantidad de cambios.

---

## 2) Protocolo de ejecucion continuo (Build -> Break -> Fix -> Harden)

### Ciclo por lote (obligatorio)
1. Seleccionar un acople legacy concreto.
2. Encapsular en puerto/adaptador sin cambiar contrato externo.
3. Ejecutar smoke + arquitectura + unit tests del area.
4. Si rompe:
- Clasificar: contrato, import, env, async, packaging, data.
- Aplicar fix minimo.
- Re-test completo del lote.
5. Documentar decision tecnica + riesgo residual.

### Definicion de "rompio"
- Error de import/boot.
- Regresion en endpoints criticos (`/`, `/health`, `/health/prewarm`, `/track/*`, `/admin/*`, `/api/identity/*`).
- Caida de test guard-rail.
- Drift de deploy (`vercel includeFiles`, templates no encontrados).

---

## 3) Chunks de trabajo restantes (detalle + por que)

## Chunk A - Eliminar dependencia interna `tracking` <-> `cache`

### Objetivo
Romper la cadena `meta_capi -> tracking -> cache` para aislar envio y deduplicacion por puertos.

### Archivos foco
- `app/tracking.py`
- `app/cache.py`
- `app/application/interfaces/cache_port.py`
- `app/infrastructure/cache/*.py`

### Pasos
1. Extraer helpers puros de `tracking.py`:
- `generate_external_id`
- `generate_fbc`
- `generate_fbp`
- `generate_event_id`
- `hash_data`
2. Mover deduplicacion/visitor-cache a `cache_port` + adapters infra.
3. Reemplazar imports de `app.cache` en `tracking.py` por dependencias inyectadas o facade interno local.
4. Mantener compat API en `tracking.py` durante transicion.

### Por que
- Hoy tracking mezcla utilidades puras con infraestructura mutable.
- Eso eleva riesgo de regresion por estado global y side effects.

### Riesgos esperados
- Duplicados de eventos si dedup cambia semantica.
- Variacion en cookies fbc/fbp.

### Mitigacion
- Tests de golden behavior para funciones de tracking.
- Test de no-duplicacion con casos idempotentes.

### Criterio de salida
- `tracking.py` sin `from app.cache ...`.
- Tests de tracking + arquitectura en verde.

---

## Chunk B - Desacoplar `meta_capi.py` de `tracking.py` y `cache.py`

### Objetivo
Convertir `meta_capi.py` en adaptador puro de salida, sin dependencia circular.

### Archivos foco
- `app/meta_capi.py`
- `app/infrastructure/external/meta_capi/tracker.py`
- `app/application/interfaces/tracker_port.py`

### Pasos
1. Mover hashing, payload build y dedup al borde de adaptador (tracker infra).
2. Inyectar estrategias:
- deduplicador (port)
- id/event utils (helper module puro)
3. Exponer wrapper de compat en `meta_capi.py` que delegue al tracker infra.

### Por que
- `meta_capi.py` hoy no es un adapter limpio; arrastra dependencias internas.
- Esa mezcla impide escalar y testear con claridad.

### Riesgos esperados
- Cambios de payload Meta (match quality).
- Falsos duplicados o falsos positivos.

### Mitigacion
- Snapshot tests de payload.
- Test de integration controlado con sandbox/test_event_code.

### Criterio de salida
- `meta_capi.py` sin import directo de `tracking` ni `cache`.
- Trackers via `TrackerPort` como ruta principal.

---

## Chunk C - Migrar servicios legacy a repositorios/ports

### Objetivo
Eliminar `app.database` de `services`, `maintenance`, `diagnostics`.

### Archivos foco
- `app/services/__init__.py`
- `app/maintenance.py`
- `app/diagnostics.py`
- `app/infrastructure/persistence/*`
- `app/interfaces/api/dependencies.py`

### Pasos
1. Definir operaciones minimas requeridas por servicios:
- lectura CMS (`site_content`)
- checks de conectividad
- consultas administrativas
2. Implementar adapters de repositorio para esas operaciones.
3. Reemplazar llamadas `legacy_database.*` por dependencias inyectadas.
4. Dejar fallback de compat solo en un punto (facade temporal).

### Por que
- Es la zona de mayor deuda operacional (startup, warm cache, mantenimiento).
- Si falla aqui, falla boot/performance.

### Riesgos esperados
- Cold start mas lento o fallas de startup por DB.
- resultados vacios de CMS si query cambia.

### Mitigacion
- conservar fallbacks in-memory/fallback content.
- validar boot integrity + smoke de `/`.

### Criterio de salida
- `services/maintenance/diagnostics` sin imports directos de `app.database`.

---

## Chunk D - Retirar facade legacy por capas

### Objetivo
Pasar de `LegacyFacade` transicional a providers por puerto.

### Archivos foco
- `app/interfaces/api/dependencies.py`
- `app/interfaces/api/routes/*.py`

### Pasos
1. Separar providers por dominio:
- provider DB admin/reporting
- provider tracking utils
- provider event sender
- provider cache visitor
2. Reemplazar llamadas genericas del facade por providers especializados.
3. Dejar `LegacyFacade` en modo compat-only y marcar deprecacion.

### Por que
- Facade centraliza deuda, pero aun es deuda.
- La salida real es puertos explicitos, no facade indefinida.

### Riesgos esperados
- wiring inconsistente por ruta.

### Mitigacion
- test contract por ruta + test de dependencias.

### Criterio de salida
- `LegacyFacade` sin uso en routes productivas.

---

## Chunk E - Cierre definitivo de modulos legacy

### Objetivo
Declarar y ejecutar `keep/remove` final por modulo legacy.

### Pasos
1. Marcar cada modulo:
- Keep permanente (si aplica)
- Compat temporal con fecha de retiro
- Remove inmediato
2. Eliminar codigo muerto y rutas de fallback obsoletas.
3. Actualizar documentacion tecnica y runbooks.

### Por que
- Sin retiro, la deuda vuelve por inercia.

### Criterio de salida
- Inventario legacy en 0 (o solo wrappers de compat explicitamente aprobados).

---

## 4) Matriz de "si se rompe" (playbook de reparacion)

### Caso 1: falla boot/import
- Sintoma: `test_app_boot_integrity` falla.
- Accion:
1. localizar modulo de import ciclico.
2. mover import a factory/dependency provider.
3. re-ejecutar boot test.

### Caso 2: templates no encontrados
- Sintoma: `health/prewarm` sin `found`.
- Accion:
1. verificar `settings.TEMPLATES_DIRS`.
2. verificar `vercel.json includeFiles`.
3. validar `api/templates/pages/public/home.html`.

### Caso 3: eventos no salen a Meta
- Sintoma: tracking OK local, sin conversion en destino.
- Accion:
1. validar payload snapshot.
2. validar dedup key.
3. validar token/pixel/test_event_code.

### Caso 4: regresion en cache/dedup
- Sintoma: duplicados o perdida de eventos.
- Accion:
1. test idempotencia por `event_id`.
2. comparar semantica TTL antes/despues.
3. activar fallback fail-open temporal.

### Caso 5: drift de configuracion pytest/test runner
- Sintoma: `quick` no corre por config incorrecta.
- Accion:
1. forzar `-c pytest.ini` root.
2. normalizar encoding consola (UTF-8 safe fallback).

---

## 5) Cadencia recomendada de entrega (2 semanas por wave)

### Wave 1 (Dias 1-4)
- Chunk A (tracking-cache)
- smoke + arquitectura + quick

### Wave 2 (Dias 5-8)
- Chunk B (meta_capi desacoplado)
- tests payload + sandbox checks

### Wave 3 (Dias 9-11)
- Chunk C (services/maintenance/diagnostics)
- validacion cold start y `/health/prewarm`

### Wave 4 (Dias 12-14)
- Chunk D + E (retiro facade y cierre legacy)
- acta de cierre tecnico

---

## 6) Checklist por PR (obligatorio)

- [ ] Scope pequeno y reversible
- [ ] Sin nuevos imports legacy directos
- [ ] Tests de area en verde
- [ ] Guard-rails arquitectura en verde
- [ ] Smoke de rutas criticas ejecutado
- [ ] Riesgo residual documentado
- [ ] Evidencia adjunta (comandos + salida)

---

## 7) Comandos estandar de validacion

Arquitectura:
```powershell
$env:PYTHONIOENCODING='utf-8'; pytest -q tests/00_architecture/test_no_legacy_paths.py -q
```

Boot + arquitectura:
```powershell
$env:PYTHONIOENCODING='utf-8'; pytest -q tests/00_architecture/test_boot_integrity.py tests/00_architecture/test_no_legacy_paths.py -q
```

Quick suite:
```powershell
python scripts/test_runner.py quick
```

Busqueda de imports legacy:
```powershell
rg -n "from app\.(database|tracking|meta_capi|cache) import|import app\.(database|tracking|meta_capi|cache)|from app import (database|tracking|meta_capi|cache)" app -g "*.py"
```

---

## 8) Criterios de exito final (Go/No-Go)

### Go (listo para cerrar refactor)
- `application` sin acoplamiento legacy.
- `interfaces/routes` sin acoplamiento legacy directo.
- `services/maintenance/diagnostics` sin `app.database` directo.
- `meta_capi` y `tracking` desacoplados de `cache` y entre si.
- `LegacyFacade` retirado o reducido a compat no productiva.
- suites clave en verde de forma repetible.

### No-Go
- cualquier dependencia circular nueva.
- cualquier regresion en rutas criticas.
- cualquier drift de templates/deploy.

---

## 9) Bitacora viva (llenar en cada iteracion)

Formato de registro:
- Fecha:
- Chunk ejecutado:
- Cambios:
- Que se rompio:
- Fix aplicado:
- Tests ejecutados:
- Resultado:
- Riesgo residual:
- Proximo paso:

---

## 10) Proximo paso inmediato sugerido

Ejecutar Chunk A completo:
1. extraer utilidades puras de tracking a modulo helper.
2. eliminar import de `app.cache` desde `app/tracking.py`.
3. validar con tests + quick suite + search de imports legacy.

