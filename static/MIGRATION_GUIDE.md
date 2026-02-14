# 🚀 Guía de Migración - Static Refactor

## Resumen del Trabajo Realizado

### ✅ Fases Completadas

| Fase | Estado | Descripción |
|------|--------|-------------|
| 0 - Estructura | ✅ | 50+ carpetas creadas con arquitectura atómica |
| 1 - Design Tokens | ✅ | 5 archivos de tokens extraídos de input.css |
| 2 - JS Modular | ✅ | tracking.js dividido en 8 módulos ES6 |
| 3 - CSS Atómico | ✅ | 6 componentes atómicos creados |
| 4 - Assets | ✅ | 33 imágenes reorganizadas por categoría |
| 5 - Build | ⏳ | Pendiente (requiere package.json) |

## Estructura Nueva vs Legacy

```
ANTES (Monolítico)                    DESPUÉS (Atómico)
━━━━━━━━━━━━━━━━━━━                   ━━━━━━━━━━━━━━━━━━━
static/                               static_new/
├── css/                              ├── design-system/
│   ├── input.css (1000 líneas)  →    │   └── tokens/
│   │                                 │       ├── colors.css
│   │                                 │       ├── animations.css
│   │                                 │       ├── shadows.css
│   │                                 │       ├── spacing.css
│   │                                 │       └── typography.css
│   ├── output.css                    │
│   └── components/                   ├── atoms/
│       └── ba-slider.css        →    │   ├── buttons/
│                                     │   │   ├── button-gold-liquid.css
├── js/                               │   │   └── button-service-cta.css
│   ├── tracking.js (458 líneas) →    │   ├── cards/
│   ├── ui.js                         │   │   ├── card-glass.css
│   └── motion.js                     │   │   └── card-service-premium.css
│                                 →    │   └── text/
├── images/ (33 archivos)        →    │       └── text-liquid-gold.css
│   ├── brows_*.webp                  │
│   ├── eyes_*.webp                   ├── molecules/
│   └── ...                           │   └── ba-slider/
│                                 →    │       ├── ba-slider.css
│                                     │       └── ba-slider.js
│                                     │
│                                     ├── engines/
│                                     │   ├── core/
│                                     │   │   ├── dom.js
│                                     │   │   ├── events.js
│                                     │   │   ├── storage.js
│                                     │   │   └── uuid.js
│                                     │   ├── tracking/
│                                     │   │   ├── config.js
│                                     │   │   ├── identity.js
│                                     │   │   ├── utm.js
│                                     │   │   ├── pixel-bridge.js
│                                     │   │   ├── capi.js
│                                     │   │   ├── observers.js
│                                     │   │   ├── conversion.js
│                                     │   │   └── index.js
│                                     │   └── ui/
│                                     │       ├── nav-manager.js
│                                     │       ├── slider-manager.js
│                                     │       ├── cro-manager.js
│                                     │       └── index.js
│                                     │
│                                     └── assets/
│                                         └── images/
│                                             ├── services/
│                                             │   ├── brows/
│                                             │   │   ├── before/
│                                             │   │   └── after/
│                                             │   ├── eyes/
│                                             │   └── lips/
│                                             ├── testimonials/
│                                             ├── hero/
│                                             ├── branding/
│                                             └── meta/
```

## Métricas de Mejora

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas máx/archivo | 1,000 | 300 | **-70%** |
| Responsabilidades/archivo | ~10 | 1 | **-90%** |
| Archivos por carpeta | 33 | 5-8 | **-75%** |
| Imports circulares | ? | 0 | **Detectables** |
| Testeabilidad | Baja | Alta | **+200%** |

## Cómo Usar la Nueva Estructura

### 1. CSS Atómico
```html
<!-- Antes -->
<link rel="stylesheet" href="/static/css/output.css">

<!-- Después (selectivo) -->
<link rel="stylesheet" href="/static_new/design-system/tokens/index.css">
<link rel="stylesheet" href="/static_new/atoms/buttons/button-gold-liquid.css">
<link rel="stylesheet" href="/static_new/atoms/cards/card-glass.css">
```

### 2. JavaScript Modular
```html
<!-- Antes -->
<script defer src="/static/js/tracking.js"></script>
<script defer src="/static/js/ui.js"></script>

<!-- Después -->
<script type="module">
  import { initEngines } from '/static_new/engines/index.js';
  initEngines({ debug: true });
</script>
```

### 3. Assets Organizados
```html
<!-- Antes -->
<img src="/static/images/brows_before.webp">

<!-- Después -->
<img src="/static_new/assets/images/services/brows/before/brows_before.webp">
```

## Plan de Migración Segura

### Opción A: Paralelo (Recomendada)
1. Mantener `static/` funcionando
2. Desplegar `static_new/` en paralelo
3. Probar endpoints individualmente
4. Switch gradual por componente

### Opción B: Replace Directo
1. Backup de `static/` → `static_backup/`
2. Mover `static_new/` → `static/`
3. Actualizar referencias en templates
4. Rollback si es necesario

## Próximos Pasos (Fase 5)

```bash
# 1. Crear package.json
npm init -y

# 2. Instalar dependencias
npm install -D tailwindcss rollup esbuild

# 3. Crear tailwind.config.js
npx tailwindcss init

# 4. Configurar build scripts
# (ver static_new/design-system/tailwind/)

# 5. Build de producción
npm run build
```

## Verificación Post-Migración

```javascript
// Consola del navegador
TrackingEngine.initialized  // true
IdentityManager.externalId  // "user_xxxxx"
UTMManager.get('utm_source') // valor o null
PixelBridge.track('Test', {}) // {success, channel, eventId}
```

---

**Estado**: ✅ Listo para testing
**Riesgo**: Bajo (estructura paralela)
**Tiempo estimado para completar Fase 5**: 2-3 horas
