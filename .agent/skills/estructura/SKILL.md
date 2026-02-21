---
name: estructura
description: Skill maestra para gestionar el esqueleto HTML, la arquitectura de plantillas Jinja2 y la organización de layouts. Úsala para cambios estructurales en el sitio.
---

# 🏗️ Skill Maestra de Estructura

## Goal
Garantizar una arquitectura de plantillas sólida, escalable y optimizada para el proyecto Jorge Aguirre Flores.

## Instructions
1. **Visión General**: Revisa la [Guía de Arquitectura](file:///home/jorand/antigravityobuntu/.agent/skills/estructura/references/ARCHITECTURE.md) para entender cómo se conectan las piezas.
2. **Sub-skills**:
   - Para cambios globales en el esqueleto: Usa [Layouts](file:///home/jorand/antigravityobuntu/.agent/skills/estructura/layouts/SKILL.md).
   - Para crear nuevas páginas o componentes: Usa [Templates](file:///home/jorand/antigravityobuntu/.agent/skills/estructura/templates/SKILL.md).
3. **Verificación**: Utiliza `scripts/structure_manager.py` para analizar la jerarquía de bloques y asegurar que la herencia sea correcta.

## Constraints
- **Protocolo Check-Before-Change (CBC) OBLIGATORIO:** NUNCA asumas que una ruta es correcta. Antes de inyectar rutas relativas o absolutas en plantillas (por ej. imágenes, CSS, scripts), DEBES verificar que el archivo existe en el sistema de archivos (`/static/...`).
- Todo debe pasar por `url_for('static', path='...')` en Jinja2. Prohibido el uso de rutas relativas simples. Si falla, reporta el error exacto antes de guardar el archivo.
- Es mandatorio mantener la coherencia con las skills de `marca` (estética) y `diseño` (componentes).
- No se deben alterar las etiquetas críticas de tracking y SEO integradas en el layout base.

## Examples
- **Usuario**: "¿Qué bloques puedo usar en la página de inicio?"
- **Agente**: Utiliza la sub-skill de layouts para listar los bloques de `base.html` y explica su función.
- **Usuario**: "Crea una nueva página de servicios."
- **Agente**: Genera la estructura HTML correcta extendiendo de la base y usando los bloques adecuados mediante la sub-skill de templates.
