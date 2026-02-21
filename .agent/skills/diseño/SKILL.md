---
name: diseño
description: Skill maestra para gestionar componentes UI, arquitectura CSS y patrones de diseño (botones, tarjetas, efectos). Úsala para consultas estéticas y modificaciones de componentes.
---

# 🎨 Skill Maestra de Diseño

## Goal
Gobernar la consistencia visual y la implementación técnica de los componentes de interfaz en el proyecto Jorge Aguirre Flores.

## Instructions
1. **Referencia de Estilo**: Consulta la [Guía de Diseño](file:///home/jorand/antigravityobuntu/.agent/skills/diseño/references/DESIGN_GUIDE.md) para entender los principios estéticos del sitio.
2. **Sub-skills**:
   - Para crear o editar botones/tarjetas: Usa [Componentes](file:///home/jorand/antigravityobuntu/.agent/skills/diseño/componentes/SKILL.md).
   - Para cambios estructurales en CSS: Usa [Estilos](file:///home/jorand/antigravityobuntu/.agent/skills/diseño/estilos/SKILL.md).
3. **Ejecución Técnica**:
   - El archivo principal de acción es [`input.css`](file:///home/jorand/antigravityobuntu/static/src/input.css).
   - Utiliza `scripts/design_manager.py` para analizar el estado actual de los componentes.

## Constraints
- Siempre debe haber coherencia absoluta con la skill `marca`.
- Los componentes deben ser responsivos y accesibles.
- Cualquier cambio estético significativo debe ser verificado visualmente (si el entorno lo permite).

## Examples
- **Usuario**: "¿Cómo es el diseño del botón principal?"
- **Agente**: Utiliza la sub-skill de componentes para leer la definición de `.btn-primary` en `input.css` y la explica al usuario.
- **Usuario**: "Crea un nuevo estilo de tarjeta para servicios."
- **Agente**: Propone una clase siguiendo el patrón de `card-glass` usando la sub-skill de estilos.
