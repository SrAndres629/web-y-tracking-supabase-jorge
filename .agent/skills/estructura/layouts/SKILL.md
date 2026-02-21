---
name: estructura-layouts
description: Sub-skill para gestionar el esqueleto base (base.html) y la estructura global del sitio. Úsala para cambios en el HEAD, navegación global o pies de página.
---

# Gestión de Layouts Globales

## Goal
Mantener la integridad y el rendimiento del esqueleto HTML principal del sitio.

## Instructions
1. **Analizar Bloques**: Antes de modificar [`base.html`](file:///home/jorand/antigravityobuntu/api/templates/layouts/base.html), usa `python3 scripts/structure_manager.py blocks layouts/base.html` para ver qué secciones están disponibles.
2. **Jerarquía**: No añadas contenido directamente en `base.html` si pertenece a una página específica; usa los bloques delegados (`content`, `extra_head`, etc.).
3. **Recursos**: Asegura que cualquier nuevo recurso (CSS/JS) en el head tenga la versión del sistema para invalidación de caché (`?v={{ system_version }}`).

## Constraints
- No eliminar bloques existentes sin verificar dependencias en las páginas que heredan de él.
- Mantener el estándar de SEO y accesibilidad en el marcado global.
