# 🚀 Static New - Atomic Architecture v3.0

## Quick Start

```bash
cd static_new
npm install
npm run build
npm run verify
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Watch mode for CSS and JS |
| `npm run build` | Production build (CSS + JS) |
| `npm run css:build` | Build CSS only |
| `npm run css:watch` | Watch CSS changes |
| `npm run js:build` | Build JS only |
| `npm run js:watch` | Watch JS changes |
| `npm run clean` | Remove dist folder |
| `npm run verify` | Verify build outputs |

## Architecture

```
static_new/
├── design-system/     # Tokens and Tailwind config
├── atoms/            # Indivisible components
├── molecules/        # Composite components
├── organisms/        # Section components
├── layouts/          # Page structures
├── engines/          # JavaScript modules
├── assets/           # Images, fonts, icons
└── dist/             # Built files (generated)
```

## Usage in Templates

### Option 1: Modern (ES Modules) - Recommended
```html
<!-- CSS -->
<link rel="stylesheet" href="/static_new/dist/css/app.min.css?v=3.0.0">

<!-- JS -->
<script type="module">
  import { TrackingEngine } from '/static_new/engines/tracking/index.js';
  TrackingEngine.init();
</script>
```

### Option 2: Legacy Bundle (Compatibility)
```html
<!-- For gradual migration from old static/ -->
<script type="module" src="/static_new/engines/legacy-adapter.js"></script>
```

### Option 3: IIFE Bundle (No modules)
```html
<!-- For older browsers -->
<script src="/static_new/dist/js/engines.bundle.min.js"></script>
<script>
  AppEngines.init();
</script>
```

## JavaScript API

### Tracking Engine
```javascript
import { TrackingEngine, handleConversion } from '/static_new/engines/tracking/index.js';

// Initialize
TrackingEngine.init({ debug: true });

// Track events
TrackingEngine.track('ViewContent', { content_name: 'Service' });

// Handle conversion (WhatsApp)
handleConversion('Hero CTA');
```

### UI Engine
```javascript
import { UIEngine } from '/static_new/engines/ui/index.js';
UIEngine.init();
```

### Motion Engine
```javascript
import { MotionEngine } from '/static_new/engines/motion/index.js';
MotionEngine.init();
```

## Design Tokens

Available CSS variables:

```css
/* Colors */
var(--luxury-gold)
var(--luxury-black)
var(--luxury-text)

/* Spacing */
var(--space-4)   /* 1rem */
var(--space-6)   /* 1.5rem */

/* Typography */
var(--font-sans)
var(--font-serif)

/* Animations */
var(--transition-spring)
animation: fade-in-up 0.8s ease-out;
```

## Migration from Old Structure

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed instructions.

### Quick Migration Path

1. **Install dependencies**
   ```bash
   cd static_new && npm install
   ```

2. **Build assets**
   ```bash
   npm run build
   ```

3. **Update templates** (gradually)
   ```html
   <!-- Before -->
   <link rel="stylesheet" href="/static/css/output.css">
   <script defer src="/static/js/tracking.js"></script>
   
   <!-- After -->
   <link rel="stylesheet" href="/static_new/dist/css/app.min.css">
   <script type="module" src="/static_new/engines/legacy-adapter.js"></script>
   ```

4. **Test and deploy**

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

For older browsers, use the IIFE bundle.

## Development

### Watch Mode
```bash
npm run dev
```

This starts:
- Tailwind CSS watcher
- Rollup JS watcher

### Adding New Components

1. Create CSS in appropriate folder:
   ```bash
   touch atoms/buttons/button-new.css
   ```

2. Import in `design-system/tailwind/input.css`:
   ```css
   @import url('../../atoms/buttons/button-new.css');
   ```

3. Create JS module:
   ```bash
   touch engines/feature/index.js
   ```

4. Add to Rollup config if needed

## Build Outputs

After `npm run build`:

```
dist/
├── css/
│   └── app.min.css          # Main CSS bundle (~50KB)
└── js/
    ├── engines.bundle.js     # ESM bundle
    ├── engines.bundle.min.js # IIFE minified
    ├── tracking.modern.js    # Tracking only (ESM)
    ├── tracking.legacy.js    # Tracking only (UMD)
    ├── ui.modern.js          # UI only (ESM)
    └── motion.modern.js      # Motion only (ESM)
```

## License

MIT
