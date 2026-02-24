# 🚀 Static Assets - Atomic Architecture v3.0

This folder is the active static layer consumed by FastAPI at `/static`.

## Quick Start

```bash
cd /workspace/web-y-tracking-supabase-jorge
npm install
npm run build:css
```

## Available Scripts (current `package.json`)

| Command | Description |
|---|---|
| `npm run build:css` | Build production CSS bundle to `static/dist/css/app.min.css` |
| `npm run watch:css` | Watch and rebuild CSS during development |
| `npm run audit:css` | Build non-minified audit CSS bundle |

## Folder Architecture

```text
static/
├── design-system/     # Tokens + Tailwind entrypoint
├── atoms/             # Atomic CSS components
├── molecules/         # Composite CSS components
├── layouts/           # Layout-level CSS
├── engines/           # JS modules (tracking/ui/motion/core)
├── assets/            # Images and branding assets
├── src/               # Tailwind input bridge
└── dist/              # Generated bundles
```

## Usage in Templates

```html
<link rel="stylesheet" href="/static/dist/css/app.min.css">
<script type="module" src="/static/engines/tracking/index.js"></script>
```

## Build Output Contract

After `npm run build:css`, the following file must exist:

- `static/dist/css/app.min.css`

This contract is validated by frontend rendering tests.
