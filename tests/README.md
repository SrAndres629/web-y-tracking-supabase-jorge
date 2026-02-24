# Testing Infrastructure - Current Layout

## Structure

```text
tests/
├── L1_atoms/          # Unit/property-level deterministic checks
├── L2_components/     # Component/service contracts
├── L3_modules/        # Concurrency + integration across modules
├── L4_integration/    # Frontend/backend integration guards
├── L4_supervisor/     # Import integrity + supervision checks
├── L5_system/         # System-level marketing and asset readiness
├── L6_omni/           # Omni-level end-to-end guards
├── frontend/          # Rendering, templates, SEO, UX checks
├── platform/          # Cloudflare, deployment, infra, observability
├── load/              # Locust performance scripts
└── cortex_audit/      # Diagnostic and auditing scripts
```

## Run by sector

```bash
pytest tests/L1_atoms tests/L2_components -v
pytest tests/L3_modules tests/L4_integration tests/L4_supervisor -v
pytest tests/L5_system tests/frontend tests/platform -v
```

## Critical deploy checks

- `tests/frontend/rendering/test_asset_delivery.py`
  Validates `/static/dist/css/app.min.css` and `/static/engines/tracking/index.js` are real assets (not HTML fallback).
- `tests/platform/deployment/test_serverless_packaging.py`
  Enforces `api/templates/**` and `static/**` in `vercel.json`.
- `tests/platform/cloudflare/test_zaraz.py`
  Validates Zaraz/CAPI/Pixel config when Cloudflare API egress is available.

## Notes

- Live external checks auto-skip when runtime blocks outbound sockets.
- `git_sync.py` deployment gates should prioritize `tests/L*`, `tests/frontend`, and `tests/platform` sectors.
