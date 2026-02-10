# 📁 Static Folder - Atomic Architecture

## Estructura de Carpetas (AI-First)

```
static_new/
├── design-system/          # Tokens y fundamentos
│   ├── tokens/            # Variables CSS atómicas
│   └── tailwind/          # Configuración Tailwind
├── atoms/                 # Elementos indivisibles
│   ├── buttons/
│   ├── cards/
│   ├── text/
│   └── icons/
├── molecules/             # Componentes compuestos
│   ├── ba-slider/
│   ├── navbar/
│   ├── process-step/
│   └── service-card/
├── organisms/             # Secciones completas
│   ├── hero/
│   ├── gallery/
│   ├── services/
│   └── testimonials/
├── layouts/               # Estructuras de página
│   └── navigation/
├── engines/               # JavaScript modular
│   ├── core/             # Utilidades (DOM, events, storage)
│   ├── tracking/         # Analytics (Zaraz + CAPI)
│   ├── ui/               # Interacciones UI
│   └── motion/           # Animaciones (GSAP)
├── assets/               # Recursos estáticos
│   ├── images/
│   ├── fonts/
│   └── icons/
└── dist/                 # Archivos compilados
    ├── css/
    └── js/
```

## Principios de Organización

### 1. Co-locación
Cada componente incluye todos sus recursos:
```
molecules/ba-slider/
├── ba-slider.css
├── ba-slider.js
└── README.md
```

### 2. Tamaño Cognitivo
- CSS: Máximo 200 líneas por archivo
- JS: Máximo 300 líneas por módulo
- Componentes: Responsabilidad única

### 3. Import Orden
```javascript
// 1. Core (no dependencias)
import { DOM } from '../core/dom.js';

// 2. Config
import { TrackingConfig } from './config.js';

// 3. Módulos del mismo nivel
import { IdentityManager } from './identity.js';

// 4. Export público
export const MyModule = { ... };
```

## Migración desde Static Legacy

| Legacy | Nuevo |
|--------|-------|
| `static/css/input.css` | `static_new/design-system/tokens/` + `atoms/` |
| `static/js/tracking.js` | `static_new/engines/tracking/` |
| `static/js/ui.js` | `static_new/engines/ui/` |
| `static/js/motion.js` | `static_new/engines/motion/` (pendiente) |
| `static/images/` | `static_new/assets/images/` (organizado) |

## Uso

### JavaScript Modular
```html
<script type="module">
  import { TrackingEngine } from '/static_new/engines/tracking/index.js';
  TrackingEngine.init();
</script>
```

### CSS Atómico
```css
/* En atoms/buttons/button-primary.css */
@import url('../../design-system/tokens/index.css');

.btn-primary {
  background: var(--gradient-gold-primary);
  box-shadow: var(--shadow-button-gold);
}
```

## Build (Fase 5)

```bash
# Instalar dependencias
npm install

# Build CSS (Tailwind + custom)
npm run css:build

# Build JS (Rollup)
npm run js:build

# Dev mode
npm run dev
```
