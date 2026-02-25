---
name: marca
description: Skill maestra para gestionar la identidad visual, visión y configuración técnica de la marca Jorge Aguirre Flores. Úsala para cualquier cambio estético, consultas sobre la marca o configuración global.
---

# 💎 Jorge Aguirre Flores - Skill Maestra de Marca

## Goal
Centralizar y coordinar la gestión de la identidad visual y técnica de la marca, asegurando la coherencia entre la visión del negocio y la implementación en código.

## Instructions
1. **Entender la Visión**: Antes de cualquier cambio, consulta la [Guía de Marca](file:///home/jorand/antigravityobuntu/.agent/skills/marca/references/BRAND_GUIDE.md) para alinearte con los objetivos.
2. **Delegar a Sub-skills**:
   - Para colores específicos: Usa la sub-skill [Colores](file:///home/jorand/antigravityobuntu/.agent/skills/marca/colores/SKILL.md).
   - Para textos y fuentes: Usa la sub-skill [Fuentes](file:///home/jorand/antigravityobuntu/.agent/skills/marca/fuentes/SKILL.md).
   - Para configuraciones de Tailwind: Usa la sub-skill [Config](file:///home/jorand/antigravityobuntu/.agent/skills/marca/config/SKILL.md).
3. **Sincronización Técnica**: Asegúrate de que los cambios se realicen en los archivos raíz:
   - [`tailwind.config.js`](file:///home/jorand/antigravityobuntu/tailwind.config.js)
   - [`colors.css`](file:///home/jorand/antigravityobuntu/static/design-system/tokens/colors.css)
   - [`typography.css`](file:///home/jorand/antigravityobuntu/static/design-system/tokens/typography.css)

## Tools & Automation
Esta skill cuenta con el script `scripts/brand_manager.py` para automatizar la actualización de tokens de color de forma segura.

## Examples
- **Usuario**: "¿Cuál es el color principal de nuestra marca?"
- **Agente**: Responde usando la Guía de Marca mencionando el *Luxury Gold* y sus objetivos de exclusividad.
- **Usuario**: "Cambia el color de oro a uno más brillante."
- **Agente**: Utiliza la sub-skill de Colores para ejecutar el script de actualización y sincronización.

## **Sincronización de Integridad Global**
- **Frontend Sync**: Provee los tokens de diseño y assets a `estructura` y `diseño`.
- **AI Sync**: Establece el "Tone of Voice" para los flujos de `genkit-orchestrator`.
- **QA Sync**: Verifica que los colores y logos mantengan el contraste reglamentario auditado por `auditoria-qa`.
