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

## **Sincronización de Integridad Global**
- **Design Sync**: Integra los componentes atómicos creados por `diseño` en los layouts de Jinja2.
- **Track Sync**: Protege los scripts de tracking definidos por `zaraz-tracking-architect`.
- **QA Sync**: Asegura que el árbol de accesibilidad (A11y) sea óptimo para las auditorías de `auditoria-qa`.

## Examples
- **Usuario**: "¿Qué bloques puedo usar en la página de inicio?"
- **Agente**: Utiliza la sub-skill de layouts para listar los bloques de `base.html` y explica su función.
- **Usuario**: "Crea una nueva página de servicios."
- **Agente**: Genera la estructura HTML correcta extendiendo de la base y usando los bloques adecuados mediante la sub-skill de templates.
