# Audit Report - Legacy Imports and Template Paths

Date: 2026-02-11
Scope: `app/**`, `api/**`, `tests/**`, `main.py`, `vercel.json`

## Executive Summary

- Status: `ARC-101` completed (automated audit baseline).
- Active blocking finding: legacy template packaging path in `vercel.json` (fixed in this cycle).
- Active migration finding: legacy template fallbacks in `app/config.py` (fixed in this cycle).
- Residual risk: legacy module tree `app/routes/**` still exists and can cause accidental reuse.

## Commands Used

- `rg -n "app\\.routes" app api tests main.py`
- `rg -n "app/templates|templates/" app api tests main.py vercel.json`
- `rg -n "includeFiles|templates|static" vercel.json`
- `rg -n "_resolve_templates_dirs\\(|TEMPLATES_DIRS|TEMPLATES_DIR" app api main.py`

## Findings

1. High - Legacy serverless include path
- File: `vercel.json`
- Evidence: `includeFiles` referenced `app/templates/**`.
- Impact: serverless build can package stale/legacy templates instead of the intended source of truth.
- Action: replaced with `api/templates/**` in both `builds` and `functions`.
- Status: fixed.

2. High - Runtime template fallback to legacy roots
- File: `app/config.py`
- Evidence: `_resolve_templates_dirs()` included legacy candidates (`templates`, `app/templates`).
- Impact: non-deterministic template resolution and environment drift.
- Action: resolver now uses `api/templates` only (local + Vercel runtime path).
- Status: fixed.

3. Medium - Legacy code path still present
- File: `main.py:164`
- Evidence: reference to `app.routes` appears as a comment, not active import.
- Impact: low runtime risk, moderate maintainability risk.
- Action: keep as historical note or remove in cleanup pass.
- Status: accepted (non-blocking).

4. Medium - Legacy folder retained
- File: `app/routes/pages.py`
- Evidence: still present in repository and references template settings.
- Impact: accidental imports may reintroduce legacy coupling.
- Action: plan deprecation/removal under `LEG-302` after confirming zero consumers.
- Status: pending.

## False Positives / Non-Blocking Matches

- `app/services/__init__.py` contains legacy wording in comments only.
- `main.py` includes legacy wording in comments only.

## Decision Log

- Source of truth for templates is `api/templates/**`.
- Packaging and runtime resolution aligned to the same root.
- A guard-rail test now enforces no legacy imports/paths in Python code.

## Updates Applied (2026-02-11)

1. `app/config.py`
- Removed legacy template fallbacks (`templates`, `app/templates`).
- Runtime resolution now targets `api/templates` only.

2. `vercel.json`
- Replaced `app/templates/**` with `api/templates/**` in all include blocks.

3. `tests/00_architecture/test_no_legacy_paths.py`
- Added architecture audit test to block:
  - imports from `app.routes`
  - string literals that point to `app/templates/...` or `templates/...`
- Added explicit assertion for `vercel.json` include paths.

4. `demo_hive.py`
- Removed (not part of web runtime nor refactor target).

## Next Tickets

- `ARC-102`: keep CI guard active and expand to additional config files if needed.
- `DEP-103`: run staging smoke tests for HTML rendering and static asset loading.
- `LEG-302`: inventory and retire `app/routes/**` after dependency confirmation.
