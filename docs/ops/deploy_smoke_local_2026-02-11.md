# DEP-103 Local Smoke Evidence

Date: 2026-02-11
Scope: Packaging and architecture smoke for serverless deploy readiness.

## Executed checks

1. `tests/00_architecture/test_boot_integrity.py`
2. `tests/00_architecture/test_template_integrity.py`
3. `tests/00_architecture/test_serverless_packaging.py`
4. `tests/00_architecture/test_no_legacy_paths.py`

## Result

- Status: PASS (10/10 tests)
- Command:
  - `PYTHONIOENCODING=utf-8 pytest -q tests/00_architecture/test_boot_integrity.py tests/00_architecture/test_template_integrity.py tests/00_architecture/test_serverless_packaging.py tests/00_architecture/test_no_legacy_paths.py -q`

## Technical notes

- `vercel.json` normalized to JSON arrays for `includeFiles`.
- `api/templates/**` and `static/**` validated as required deploy artifacts.
- Legacy template include path `app/templates/**` is absent.
- `/health/prewarm` endpoint smoke check is active in architecture tests.

## Remaining for full DEP-103 closure

- Staging deploy verification (real serverless runtime).
- Production smoke after deploy window.
