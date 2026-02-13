# 🚀 Guía de Migración: static → static_new

## Overview

Esta guía te llevará paso a paso para migrar desde la estructura antigua (`static/`) a la nueva arquitectura atómica (`static_new/`).

---

## Paso 1: Instalar Dependencias

```bash
cd static_new
npm install
```

Esto instalará:
- `tailwindcss` - Para procesar CSS
- `rollup` - Para bundle de JavaScript
- `concurrently` - Para correr watchers en paralelo
- `autoprefixer` y `cssnano` - Para optimización CSS

---

## Paso 2: Build de Producción

```bash
npm run build
```

Esto generará:
- `static_new/dist/css/app.min.css`
- `static_new/dist/js/engines.bundle.min.js`

Verifica que todo salió bien:
```bash
npm run verify
```

---

## Paso 3: Migrar Templates (Automático)

### Modo Dry Run (Recomendado primero)
```bash
cd static_new
node scripts/migrate-templates.js ../templates
```

Esto mostrará qué cambios se harían sin modificarlos.

### Aplicar Cambios
```bash
node scripts/migrate-templates.js ../templates --apply
```

---

## Paso 4: Cambio en Base Template

Edita `templates/layouts/base.html`:

### CSS (Reemplazar)
```html
<!-- ANTES -->
<link rel="stylesheet" href="/static/css/output.css?v={{ system_version }}">

<!-- DESPUÉS -->
<link rel="stylesheet" href="/static_new/dist/css/app.min.css?v=3.0.0">
```

### JavaScript (Reemplazar)
```html
<!-- ANTES -->
<script defer src="/static/js/tracking.js?v={{ system_version }}"></script>
<script defer src="/static/js/ui.js?v={{ system_version }}"></script>
<script defer src="/static/js/motion.js?v={{ system_version }}"></script>

<!-- DESPUÉS (Opción 1: Legacy Adapter - Recomendado) -->
<script type="module" src="/static_new/engines/legacy-adapter.js"></script>

<!-- O DESPUÉS (Opción 2: ESM Moderno) -->
<script type="module">
  import { initEngines } from '/static_new/engines/index.js';
  initEngines({ debug: location.search.includes('debug') });
</script>
```

### Imágenes (Reemplazar)
```html
<!-- ANTES -->
<img src="/static/images/brows_before.webp">

<!-- DESPUÉS -->
<img src="/static_new/assets/images/services/brows/before/brows_before.webp">
```

---

## Paso 5: Actualizar Rutas en Backend (si aplica)

Si tu aplicación FastAPI sirve archivos estáticos:

```python
# app/config.py o main.py
from fastapi.staticfiles import StaticFiles

# Agregar nueva ruta estática
app.mount("/static_new", StaticFiles(directory="static_new"), name="static_new")

# Mantener vieja durante transición
app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

## Paso 6: Testing

### Verificar en Navegador

1. Abrir la página
2. Consola del navegador:
   ```javascript
   TrackingEngine.initialized  // true
   IdentityManager.externalId  // "user_xxxxx"
   ```

3. Verificar que:
   - [ ] El CSS se carga correctamente
   - [ ] Los botones tienen animaciones
   - [ ] El navbar tiene efecto glass
   - [ ] Los sliders funcionan
   - [ ] WhatsApp redirige correctamente

### Regresión Visual

Comparar screenshots antes/después:
- Homepage
- Mobile (< 768px)
- Desktop (> 1024px)

---

## Paso 7: Deploy a Producción

### Opción A: Blue-Green (Recomendado)
1. Deploy con ambas carpetas (`static/` y `static_new/`)
2. Probar en producción con flag de feature
3. Cambiar a `static_new/` cuando esté validado
4. Remover `static/` antigua

### Opción B: Directo
1. Renombrar `static/` → `static_backup/`
2. Renombrar `static_new/` → `static/`
3. Actualizar todas las referencias en templates
4. Deploy

---

## Rollback (Si algo sale mal)

```bash
# Restaurar backup
cd ..
mv static_new static_new_failed
mv static_backup static

# O simplemente cambiar templates de vuelta
# Editar templates/layouts/base.html
# Revertir cambios de rutas
```

---

## Solución de Problemas

### Error: "Cannot find module"
```bash
# Reinstalar dependencias
cd static_new
rm -rf node_modules
npm install
```

### Error: "Cannot resolve import"
```bash
# Rebuild
npm run clean
npm run build
```

### CSS no aplica
- Verificar que `dist/css/app.min.css` existe
- Verificar versión en query string `?v=3.0.0`
- Hard refresh (Ctrl+F5)

### JS no funciona
- Verificar `type="module"` en script tags
- Verificar que no hay errores en consola
- Verificar que el orden de carga es correcto (CSS primero)

---

## Beneficios de la Migración

| Aspecto | Antes | Después |
|---------|-------|---------|
| Cache busting | Manual | Automático con hashes |
| Build time | ? | ~2 segundos |
| Bundle size | Variable | Optimizado |
| Modularidad | Baja | Alta (ES6) |
| Mantenibilidad | Difícil | Fácil |
| Testing | Complejo | Unitario |

---

## Soporte

Para problemas o preguntas:
1. Revisar `static_new/README.md`
2. Revisar `static_new/MIGRATION_GUIDE.md`
3. Verificar `static_new/INDEX.md` para referencia API

---

**Fecha**: 2026-02-10  
**Versión**: 3.0.0  
**Estado**: Listo para producción
