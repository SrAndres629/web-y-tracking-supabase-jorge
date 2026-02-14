# Testing Infrastructure - Sectorized

## Structure

```
tests/
├── backend/
│   ├── architecture/   # Boot, dependency rules, clean architecture
│   ├── unit/           # Pure unit tests (domain/app logic)
│   ├── integration/    # API/application integration
│   ├── security/       # Security controls
│   ├── quality/        # Health, coverage, data flow, DB state
│   └── fuzzing/        # Input fuzzing
├── frontend/
│   ├── rendering/      # Browser render + asset delivery checks
│   ├── templates/      # Jinja/template integrity + tracking template guards
│   ├── ux/             # UX and motion integrity
│   └── seo/            # Robots/sitemap/SEO output
└── platform/
    ├── cloudflare/     # Zaraz/Cloudflare integration
    ├── infra/          # Redis/Supabase/Upstash/performance env checks
    ├── deployment/     # Vercel manifest/contracts
    ├── observability/  # Live infrastructure audits
    ├── mutation/       # Mutation scripts
    └── diagnostics/    # AI/system diagnostics
```

## Run by sector

```bash
pytest tests/frontend -v
pytest tests/backend -v
pytest tests/platform -v
```

## Critical deploy checks

- `tests/frontend/rendering/test_asset_delivery.py`
  Validates `/static/dist/css/app.min.css` and `/static/engines/legacy-adapter.js` are real assets (not HTML fallback).
- `tests/platform/deployment/test_serverless_packaging.py`
  Enforces `api/templates/**` and `static/**` in `vercel.json`.
- `tests/platform/cloudflare/test_zaraz.py`
  Validates Zaraz/CAPI/Pixel config when Cloudflare API egress is available.

## Notes

- Live external checks auto-skip when runtime blocks outbound sockets.
- `git_sync.py` gates now execute by sectorized paths.
