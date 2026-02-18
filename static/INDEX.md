# 📚 Static New - Índice Completo

## Resumen Ejecutivo

```
📦 Proyecto: Jorge Aguirre Flores Web v3.0
🎯 Arquitectura: Atomic Design + ES6 Modules
📊 Tamaño: 3,120 líneas de código
🔧 Build: Tailwind CSS + Rollup
```

---

## 📁 Estructura de Archivos

### 🎨 Design System (7 archivos)

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `tokens/index.css` | 15 | Importador de tokens |
| `tokens/colors.css` | 115 | Paleta de colores luxury |
| `tokens/animations.css` | 155 | Keyframes y timing |
| `tokens/shadows.css` | 117 | Sombras y efectos |
| `tokens/spacing.css` | 100 | Espaciados y z-index |
| `tokens/typography.css` | 140 | Fuentes y textos |
| `tailwind/input.css` | 295 | Entry point Tailwind |

### ⚛️ Atoms (5 archivos)

| Archivo | Propósito |
|---------|-----------|
| `atoms/buttons/button-gold-liquid.css` | CTA principal con animación |
| `atoms/buttons/button-service-cta.css` | Botón de servicio |
| `atoms/cards/card-glass.css` | Tarjeta glassmorphism |
| `atoms/cards/card-service-premium.css` | Tarjeta de servicio |
| `atoms/text/text-liquid-gold.css` | Texto dorado animado |

### ⚡ Engines - Core (4 archivos)

| Archivo | Propósito | Público |
|---------|-----------|---------|
| `engines/core/dom.js` | Selectores, observers, throttle/debounce | `DOM` |
| `engines/core/events.js` | EventBus centralizado | `EventBus`, `Events` |
| `engines/core/storage.js` | Cookies, local/sessionStorage | `Storage` |
| `engines/core/uuid.js` | Generadores UUID | `UUID` |

### ⚡ Engines - Tracking (8 archivos)

| Archivo | Propósito | Público |
|---------|-----------|---------|
| `tracking/config.js` | Configuración central | `TrackingConfig` |
| `tracking/identity.js` | UUIDs, cookies, external_id | `IdentityManager` |
| `tracking/utm.js` | Parámetros UTM | `UTMManager` |
| `tracking/pixel-bridge.js` | Abstracción Zaraz/fbq | `PixelBridge` |
| `tracking/capi.js` | Server-side tracking | `CAPI` |
| `tracking/observers.js` | ViewContent, sliders | `TrackingObservers` |
| `tracking/conversion.js` | WhatsApp handlers | `ConversionHandler` |
| `tracking/index.js` | Entry point | `TrackingEngine` |

### ⚡ Engines - UI (4 archivos)

| Archivo | Propósito | Público |
|---------|-----------|---------|
| `ui/nav-manager.js` | Navbar scroll | `NavManager` |
| `ui/slider-manager.js` | BA sliders | `SliderManager` |
| `ui/cro-manager.js` | WhatsApp tooltip | `CROManager` |
| `ui/index.js` | Entry point | `UIEngine` |

### ⚡ Engines - Motion (6 archivos)

| Archivo | Propósito | Público |
|---------|-----------|---------|
| `motion/lenis-setup.js` | Smooth scroll | `LenisSetup` |
| `motion/hero-animation.js` | Hero entrance | `HeroAnimation` |
| `motion/parallax.js` | Parallax effects | `Parallax` |
| `motion/magnetic.js` | Magnetic buttons | `Magnetic` |
| `motion/spotlight.js` | Cursor glow | `Spotlight` |
| `motion/index.js` | Entry point | `MotionEngine` |

### 🛠️ Configuración (4 archivos)

| Archivo | Propósito |
|---------|-----------|
| `package.json` | Dependencias y scripts |
| `tailwind.config.js` | Configuración Tailwind |
| `rollup.config.js` | Configuración Rollup |
| `postcss.config.js` | Configuración PostCSS |

### 🔧 Scripts (2 archivos)

| Archivo | Propósito |
|---------|-----------|
| `scripts/verify-build.js` | Verifica builds |
| `scripts/migrate-templates.js` | Migra templates |

### 📚 Documentación (3 archivos)

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Guía de uso rápido |
| `MIGRATION_GUIDE.md` | Guía de migración completa |
| `INDEX.md` | Este archivo |

---

## 🚀 API Pública

### Tracking Engine

```javascript
// Inicializar
TrackingEngine.init({ debug: true });

// Track events
TrackingEngine.track('ViewContent', { content_name: 'Service' });
TrackingEngine.trackCustom('SliderInteraction', { service_id: 'brows' });

// Convert (WhatsApp)
handleConversion('Hero CTA');

// Acceso a módulos
IdentityManager.externalId;  // "user_xxx"
UTMManager.get('utm_source'); // valor o null
PixelBridge.track('Lead', {});
CAPI.trackAsync('Event', {});
```

### UI Engine

```javascript
UIEngine.init();
NavManager.init();
SliderManager.init();
CROManager.init();
```

### Motion Engine

```javascript
MotionEngine.init();
// Requiere GSAP y Lenis cargados
```

### Core Utilities

```javascript
// DOM
DOM.$('.selector');           // querySelector
DOM.$$('.selector');          // querySelectorAll (Array)
DOM.ready(callback);          // DOMContentLoaded
DOM.observe(el, callback);    // IntersectionObserver

// Events
EventBus.on('event', callback);
EventBus.emit('event', data);
EventBus.once('event', callback);

// Storage
Storage.cookies.get('name');
Storage.cookies.set('name', 'value', 30);
Storage.local.get('key', defaultValue);
Storage.session.get('key');

// UUID
UUID.generate();      // UUID v4
UUID.short('prefix'); // "prefix_abc123"
```

---

## 🎨 CSS Tokens

### Colores
```css
var(--luxury-gold)        /* #C5A059 */
var(--luxury-gold-light)  /* #E5C585 */
var(--luxury-gold-dark)   /* #B08D45 */
var(--luxury-black)       /* #050505 */
var(--luxury-text)        /* #f5f5f7 */
```

### Animaciones
```css
var(--transition-spring)   /* cubic-bezier(0.2, 0.8, 0.2, 1) */
var(--duration-normal)     /* 0.3s */
animation: fade-in-up 0.8s ease-out;
animation: pulse-gold 2s ease-in-out infinite;
```

### Espaciado
```css
var(--space-4)   /* 1rem (16px) */
var(--space-6)   /* 1.5rem (24px) */
var(--space-8)   /* 2rem (32px) */
```

### Sombras
```css
var(--shadow-gold-sm)
var(--shadow-glass)
var(--shadow-card)
```

---

## 📦 Build Outputs

Después de `npm run build`:

```
dist/
├── css/
│   └── app.min.css          (~50KB) - Todo el CSS
└── js/
    ├── engines.bundle.js     - ESM completo
    ├── engines.bundle.min.js - IIFE minificado
    ├── tracking.modern.js    - Tracking ESM
    ├── tracking.legacy.js    - Tracking UMD
    ├── ui.modern.js          - UI ESM
    └── motion.modern.js      - Motion ESM
```

---

## 🔄 Flujo de Trabajo

### Desarrollo
```bash
cd static_new
npm install
npm run dev          # Watch mode
```

### Producción
```bash
npm run build        # Build completo
npm run verify       # Verificar outputs
```

### Migración
```bash
node scripts/migrate-templates.js ../templates --dry-run
node scripts/migrate-templates.js ../templates --apply
```

---

## 🎯 Patrones de Uso

### 1. Componente Nuevo (CSS)
```css
/* atoms/componentes/mi-componente.css */
@import url('../../design-system/tokens/index.css');

.mi-componente {
  background: var(--luxury-gold);
  transition: all var(--transition-spring);
}
```

Agregar a `input.css`:
```css
@import url('../../atoms/componentes/mi-componente.css');
```

### 2. Módulo Nuevo (JS)
```javascript
// engines/mi-modulo/index.js
import { DOM } from '../core/dom.js';

export const MiModulo = {
  init() {
    // código
  }
};
```

Agregar a `rollup.config.js` si necesita bundle separado.

---

## ✅ Checklist de Calidad

- [ ] CSS: Máximo 200 líneas por archivo
- [ ] JS: Máximo 300 líneas por módulo
- [ ] Nombres descriptivos (kebab-case para CSS, camelCase para JS)
- [ ] Imports ordenados: core → config → módulos
- [ ] Exports explícitos (no default exports genéricos)
- [ ] Documentación JSDoc para funciones públicas
- [ ] Manejo de errores en operaciones async

---

## 📊 Métricas

| Aspecto | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Archivos CSS | 3 | 13 | +333% organización |
| Archivos JS | 3 | 29 | +867% modularidad |
| Líneas/archivo max | 1,000 | 300 | -70% complejidad |
| Tamaño bundle CSS | ? | ~50KB | Predecible |
| Cache hit rate | Baja | Alta | Versionado |

---

**Versión**: 3.0.0
**Última actualización**: 2026-02-10
**Estado**: ✅ Producción lista
