# LEG-302 Inventory - Legacy Compatibility Modules

Date: 2026-02-11  
Scope: `app/database.py`, `app/tracking.py`, `app/meta_capi.py`, `app/cache.py`

## Executive Summary

- Application layer direct coupling to legacy modules has been reduced in this cycle:
  - `app/application/**` no longer imports `app.database`, `app.tracking`, or `app.meta_capi` directly.
- Interface routes no longer import legacy modules directly; usage is centralized behind a facade.
- Legacy modules still depend on each other internally (`meta_capi -> tracking/cache`, `tracking -> cache`).

## Current Usage Snapshot (app only)

Pattern scanned:
- `from app.(database|tracking|meta_capi|cache) import ...`
- `import app.(database|tracking|meta_capi|cache)`
- `from app import (database|tracking|meta_capi|cache)`

Findings:
- `app/application/**`: 0 direct imports (closed for this phase)
- `app/interfaces/api/routes/**`: 0 direct imports to legacy modules
- `app/interfaces/api/dependencies.py`: centralized transitional entrypoint (`LegacyFacade`)
  - currently imports only `app.database` and `app.meta_capi`
  - no direct dependency on `app.tracking` or `app.cache`
- `app/services/**`, `app/diagnostics.py`, `app/maintenance.py`: compatibility usage remains
- Legacy-to-legacy dependencies remain inside `app/meta_capi.py` and `app/tracking.py`

Module-level direct legacy import footprint (latest scan):
- `app/tracking.py` -> `app.cache`
- `app/meta_capi.py` -> `app.tracking`, `app.cache`
- `app/services/__init__.py` -> `app.database`, `app.cache`
- `app/maintenance.py` -> `app.database`
- `app/diagnostics.py` -> `app.database`
- `app/retry_queue.py` -> `app.meta_capi`
- `app/interfaces/api/dependencies.py` -> `app.database`, `app.meta_capi`

## Module Decisions (Keep / Migrate / Remove)

1. `app/database.py`
- Status: `KEEP (transitional)` + `MIGRATE consumers`
- Why:
  - Still required by interface routes and operational utilities.
  - Existing infra repos are not yet full replacement for all CRUD/reporting helpers.
- Action:
  - Continue moving reads/writes into repositories and ports.
  - Keep this module as compatibility adapter until coverage parity.

2. `app/tracking.py`
- Status: `KEEP (transitional)` + `MIGRATE generators/webhook calls`
- Why:
  - Routes use helpers such as `generate_external_id`, `send_n8n_webhook`.
  - Identity flow now injects these functions from interface layer instead of importing in application commands.
- Action:
  - Extract generator/webhook capabilities to explicit application ports.

3. `app/meta_capi.py`
- Status: `KEEP (transitional)` + `MIGRATE event sending`
- Why:
  - Interface routes currently call `send_elite_event`.
  - Application commands no longer import this directly after dependency injection refactor.
- Action:
  - Replace route-level direct calls with `TrackerPort` implementations progressively.

4. `app/cache.py`
- Status: `KEEP (transitional)` + `MIGRATE cache operations`
- Why:
  - Used by pages route and by legacy tracking/meta stack.
  - Infrastructure cache ports exist and should become canonical.
- Action:
  - Move route and service calls toward `application/interfaces/cache_port.py`.

## Refactor Applied in This Cycle

Application-layer decoupling:
- `app/application/commands/identity/process_google_onetap_command.py`
  - Replaced direct legacy imports with injected dependencies:
    - `external_id_generator`
    - `event_sender`
- `app/application/commands/identity/track_whatsapp_redirect_command.py`
  - Same dependency injection pattern.
- `app/application/commands/admin/confirm_sale_command.py`
  - Replaced direct legacy imports with injected:
    - `get_visitor_by_id`
    - `event_sender`
- `app/application/queries/admin/get_all_visitors_query.py`
  - Injected `list_visitors` callable.
- `app/application/queries/admin/get_signal_audit_query.py`
  - Injected `get_cursor` callable.

Interface wiring updates:
- `app/interfaces/api/routes/identity.py`
  - Injects `generate_external_id` and `send_elite_event` into handlers.
- `app/interfaces/api/routes/admin.py`
  - Injects database/meta callables into query/command instances.

Interface consolidation updates:
- Added `LegacyFacade` in `app/interfaces/api/dependencies.py`.
- Updated routes to consume facade instead of importing legacy modules directly:
  - `app/interfaces/api/routes/health.py`
  - `app/interfaces/api/routes/admin.py`
  - `app/interfaces/api/routes/identity.py`
  - `app/interfaces/api/routes/pages.py`
  - `app/interfaces/api/routes/tracking.py`
- LegacyFacade internals now use:
  - local deterministic `external_id` generation
  - local visitor cache (TTL in-memory)
  - direct `httpx` webhook dispatch for n8n
  - transitional imports only for DB/meta event senders

## Risk Register

- Medium: Legacy facade still proxies to legacy modules (transitional dependency).
- Medium: Legacy modules remain interdependent (`meta_capi`, `tracking`, `cache`).
- Low: Functional regressions from DI refactor (smoke and quick tests passed in this cycle).

## Validation Evidence

- `pytest -q tests/00_architecture/test_boot_integrity.py tests/00_architecture/test_no_legacy_paths.py -q` -> PASS
- `python scripts/test_runner.py quick` -> PASS

## Next Phase (LEG-302.2)

1. Introduce explicit application ports for:
- external ID generation
- outbound conversion-event dispatch
- webhook dispatch

2. Move interface route calls from legacy modules to:
- `TrackerPort` implementations
- cache/database ports/repositories

3. Keep legacy modules as compatibility facades only, then retire once parity and tests are complete.
