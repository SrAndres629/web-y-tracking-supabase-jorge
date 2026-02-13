# Roadmap Senior de Desarrollo - Cierre de Refactor v3.0

Fecha: 2026-02-11
Alcance: Cerrar el 18% pendiente de la refactorizacion y completar el hardening operativo de plataforma.
Duracion: 6 semanas (3 sprints de 2 semanas)
Modelo: Clean Architecture + DDD + CQRS + entrega continua con gates de calidad.

## 1) North Star y objetivos medibles

Objetivo primario:
- Completar la migracion funcional hacia arquitectura limpia sin dependencia activa de paths legacy.

Resultados clave (OKRs tecnicos):
- KR1: 0 imports activos hacia `app/routes/*`, `templates/`, `app/templates/`.
- KR2: Cobertura de handlers (`app/application/commands/*`, `app/application/queries/*`) >= 80%.
- KR3: `/health/prewarm` validado en staging y produccion con diagnostico completo y estable.
- KR4: Deploy serverless sin faltantes de templates/static (0 errores 500 por assets/paths).
- KR5: Mantener o mejorar baseline de confiabilidad (sin regresion en error rate y latencia p95).

## 2) Gobernanza de ejecucion (estilo senior)

Cadencia:
- Daily: 15 min, foco en bloqueos y riesgo.
- Refinamiento: 2 veces por semana.
- Demo/retro: fin de sprint.
- Release train: 1 release semanal con ventana fija.

Reglas de merge:
- No merge sin tests y sin evidencia de acceptance criteria.
- PRs pequenas y reversibles (<400 lineas netas recomendado).
- Todo cambio estructural con ADR corto (contexto, decision, tradeoffs).

Quality gates CI:
- `pytest` obligatorio.
- Lint/type checks (si estan activos en pipeline).
- Check automatico anti-legacy-imports.

## 3) Sprints y entregables

### Sprint 1 (Semanas 1-2) - Saneamiento arquitectonico y auditoria final

Meta:
- Eliminar deuda de imports/paths legacy y dejar linea base de despliegue limpia.

Historias/Tickets:

1. ARC-101 - Auditoria automatizada de imports legacy
- Alcance:
  - Detectar referencias a `app/routes/*`, `templates/`, `app/templates/`.
  - Generar reporte por archivo con severidad.
- Archivos objetivo:
  - `app/**`
  - `api/**`
  - `tests/**`
- Criterios de aceptacion:
  - Reporte versionado en repo (ej. `docs/audit/imports_legacy_report.md`).
  - Lista de falsos positivos documentada.

2. ARC-102 - Remediacion de imports/rutas legacy
- Alcance:
  - Migrar imports a `app/interfaces/api/routes` y `app/interfaces/api/middleware`.
  - Eliminar shadowing por nombres duplicados.
- Archivos objetivo:
  - `main.py`
  - `api/index.py`
  - `app/interfaces/api/routes/*.py`
  - Cualquier consumidor detectado en ARC-101
- Criterios de aceptacion:
  - Busqueda global sin coincidencias legacy activas.
  - App inicia sin errores de import en entorno local/staging.

3. DEP-103 - Verificacion de empaquetado serverless
- Alcance:
  - Revisar `vercel.json` includeFiles para `api/templates/**` y `static/**`.
  - Validar no duplicidad conflictiva con roots antiguos.
- Archivos objetivo:
  - `vercel.json`
  - `requirements.txt`
- Criterios de aceptacion:
  - Build de staging exitoso.
  - Smoke test de paginas y assets sin 500.

Entregables Sprint 1:
- Reporte de auditoria legacy.
- PRs de migracion de imports.
- Checklist de packaging serverless firmado.

### Sprint 2 (Semanas 3-4) - Red de seguridad de calidad (tests)

Meta:
- Blindar comportamiento de comandos/queries e invariantes de dominio.

Historias/Tickets:

1. TST-201 - Harness de tests para Clean Architecture
- Alcance:
  - Base fixtures para handlers.
  - Repositorios InMemory para unit tests.
  - Mocks de integraciones externas (Meta CAPI, RudderStack).
- Archivos objetivo:
  - `tests/unit/**`
  - `tests/fakes/**` (si no existe, crearlo)
- Criterios de aceptacion:
  - Estructura reusable para commands/queries.
  - Ejecucion estable y deterministic tests.

2. TST-202 - Unit tests de Command Handlers
- Alcance:
  - Casos happy path + errores de validacion + fallos de infraestructura.
  - Cobertura de `app/application/commands/*`.
- Archivos objetivo:
  - `app/application/commands/**`
  - `tests/unit/application/commands/**`
- Criterios de aceptacion:
  - Cobertura commands >= 80% (line/branch segun pipeline).
  - Casos de deduplicacion y side effects cubiertos.

3. TST-203 - Unit tests de Query Handlers + invariantes dominio
- Alcance:
  - Cobertura de `app/application/queries/*`.
  - Tests de Value Objects (`Email`, `Phone`, `EventId`).
- Archivos objetivo:
  - `app/application/queries/**`
  - `app/domain/models/values.py`
  - `tests/unit/application/queries/**`
  - `tests/unit/domain/**`
- Criterios de aceptacion:
  - Cobertura queries >= 80%.
  - Invariantes de dominio protegidas por tests negativos/positivos.

Entregables Sprint 2:
- Suite unitaria completa y estable.
- Reporte de cobertura.
- Matriz de riesgo de regresion reducida.

### Sprint 3 (Semanas 5-6) - Hardening de produccion y cierre

Meta:
- Validar operacion real, completar migracion de compatibilidad legacy y cerrar refactor.

Historias/Tickets:

1. OPS-301 - Deploy de diagnostico prewarm
- Alcance:
  - Ejecutar deploy con endpoint `/health/prewarm` operativo.
  - Validar campos: `templates_dir`, `search_paths`, `cwd`, `base_dir`, stacktrace con `filename:line`.
- Archivos objetivo:
  - `app/interfaces/api/middleware/error_handler.py`
  - rutas health/prewarm relacionadas
- Criterios de aceptacion:
  - Respuesta JSON valida en staging y produccion.
  - Evidencia adjunta en `docs/ops/prewarm_validation.md`.

2. LEG-302 - Consolidacion final de modulos legacy
- Alcance:
  - Inventariar uso real de `app/database.py`, `app/tracking.py`, `app/meta_capi.py`, `app/cache.py`.
  - Migrar consumidores a puertos `application/interfaces/*` donde aplique.
  - Documentar modulo que permanece por compatibilidad y por que.
- Archivos objetivo:
  - modulos legacy mencionados
  - consumidores detectados en `app/**`
- Criterios de aceptacion:
  - Inventario publicado y estado de cada modulo (keep/migrate/remove).
  - Reduccion cuantificada de acoplamiento legacy.

3. REL-303 - Go/No-Go y cierre formal
- Alcance:
  - Ejecutar checklist de release.
  - Validar KPIs vs baseline.
  - Cerrar ADRs/documentacion de arquitectura.
- Archivos objetivo:
  - `code.md`
  - `REFACTOR_SUMMARY.md`
  - runbooks operativos
- Criterios de aceptacion:
  - Decision Go/No-Go documentada con evidencia.
  - Refactor marcado como cerrado con riesgos residuales explicitados.

Entregables Sprint 3:
- Validacion prewarm en prod.
- Informe de consolidacion legacy.
- Acta de cierre tecnico de refactor.

## 4) Backlog tecnico priorizado

Prioridad P0 (bloquea cierre):
- ARC-102 remediacion completa de imports legacy.
- TST-202/TST-203 cobertura de handlers e invariantes.
- OPS-301 validacion prewarm en entornos reales.

Prioridad P1:
- DEP-103 hardening de packaging/deploy.
- LEG-302 migracion de consumidores legacy de alto trafico.

Prioridad P2:
- Limpieza final de modulos obsoletos.
- Ajustes de performance y deuda secundaria.

## 5) RACI minimo (roles)

- Tech Lead:
  - Owner de arquitectura, ADRs, Go/No-Go.
- Backend Engineer:
  - Owner de migraciones de imports, handlers y tests.
- QA/SET:
  - Owner de estrategia de pruebas, cobertura y smoke tests.
- DevOps/Platform:
  - Owner de deploy, packaging y validacion en staging/prod.

## 6) Riesgos y mitigaciones

Riesgo 1: Regresion por cambios transversales.
- Mitigacion: PRs atomicos, feature flags cuando aplique, rollback por modulo.

Riesgo 2: Inconsistencias en serverless packaging.
- Mitigacion: validacion de `vercel.json` + smoke tests post-deploy obligatorios.

Riesgo 3: Dependencia oculta de modulos legacy.
- Mitigacion: auditoria de dependencias + inventario LEG-302 con decisiones explicitas.

Riesgo 4: Cobertura insuficiente en logica critica.
- Mitigacion: gate de cobertura minima y enforcement en CI.

## 7) KPIs y dashboard de seguimiento

KPIs primarios:
- `% imports legacy activos` (target: 0).
- `Coverage handlers` (target: >= 80%).
- `5xx rate` en rutas criticas (target: sin regresion o mejor).
- `p95 latency` (target: sin regresion).
- `Lead time PR->merge` (target: <24h promedio laboral).

KPIs secundarios:
- `Rollback count` por release.
- `Incidentes por paths/templates`.
- `MTTR` de incidentes relacionados a deploy.

## 8) Definition of Done (DoD) de cierre de refactor

Se considera cerrado cuando:
- No hay imports legacy activos ni shadowing de rutas.
- `/health/prewarm` esta validado en staging y produccion con evidencia.
- Tests unitarios de commands/queries e invariantes de dominio pasan en CI y cumplen cobertura objetivo.
- Packaging serverless verificado para templates/static sin errores 500.
- Documentacion final actualizada (`code.md`, resumen de refactor, runbooks, ADRs).

## 9) Checklist operativo por release semanal

- [ ] Auditoria de imports ejecutada y sin nuevos hallazgos P0.
- [ ] Suite de tests pasa en CI.
- [ ] Cobertura en umbral acordado.
- [ ] Smoke tests en staging exitosos.
- [ ] Validacion de templates/static empaquetados.
- [ ] Plan de rollback preparado.
- [ ] Aprobacion Tech Lead + Platform.

## 10) Primeras 72 horas (plan de arranque inmediato)

Dia 1:
- Ejecutar ARC-101 y abrir issues por archivo.
- Definir baseline de KPIs (error rate, latencia, cobertura).

Dia 2:
- Atacar ARC-102 por lotes pequenos.
- Ajustar `vercel.json`/packaging en rama dedicada si hay hallazgos.

Dia 3:
- Crear harness TST-201.
- Implementar primeros tests de handlers criticos (top rutas de negocio).

---

Estado inicial sugerido del roadmap: En ejecucion.
Owner recomendado del roadmap: Tech Lead + Backend principal.

