# Clean Architecture Agent Playbook

## Objective

Provide a predictable architecture that is easy for humans and coding agents to reason about, change safely, and test quickly.

## Mental Model (Agent-Oriented)

Use a strict "Think in 4 passes" routine for every change:

1. **Boundary pass**
   - What layer is being modified? (`interfaces`, `application`, `domain`, `infrastructure`)
   - Which dependency direction is allowed?
2. **Contract pass**
   - What DTO, repository port, or settings contract can break?
   - What backward compatibility alias still exists?
3. **Failure pass**
   - How does this fail in serverless mode?
   - What fallback exists (Redis missing, Postgres missing, Cloudflare missing)?
4. **Verification pass**
   - Which test sector validates the change (`tests/L*`, `tests/frontend`, `tests/platform`)?

## Current Layer Responsibilities

- `app/interfaces/`: HTTP routes, response mapping, request extraction.
- `app/application/`: use-cases, commands, handlers, orchestration.
- `app/domain/`: entities, invariants, repository interfaces.
- `app/infrastructure/`: adapters (Postgres, Redis, Meta, Cloudflare, external APIs).
- `app/middleware/`: cross-cutting runtime concerns.

## Refactoring Rules

1. Keep route files thin: parse request -> call handler -> map response.
2. Move business rules from route/helpers into `application` handlers.
3. Keep domain pure (no network, no framework imports).
4. Put all third-party I/O in infrastructure adapters.
5. Keep legacy bridges explicit and temporary (`LegacyFacade`).

## Directory Hygiene Rules

Treat these as disposable/debug artifacts (do not keep in main branches):
- ad-hoc `debug_*.json` traces
- one-off `*_out.txt` dumps
- duplicated docs that contradict active runtime paths

## Configuration Path Rules

- Single source of truth: `app/infrastructure/config/settings.py`.
- Runtime compatibility aliases can exist in `app/config.py`, but must map 1:1 correctly.
- Template path authority: `api/templates/**`.
- Static path authority: `static/**`.

## Recommended Next Cleanup Milestones

1. Reduce `LegacyFacade` calls inside route modules by introducing explicit application handlers.
2. Split long route files (`pages.py`, `tracking.py`) into cohesive modules by endpoint family.
3. Add architecture tests that enforce no infrastructure imports inside `domain`.
4. Add docs lint to detect invalid folder references in markdown (`static_new`, `tests/backend`, etc.).
