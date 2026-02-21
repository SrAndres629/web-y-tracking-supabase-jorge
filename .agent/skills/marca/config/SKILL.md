---
name: marca-config
description: Sub-skill para gestionar la configuración técnica global de la marca, incluyendo tailwind.config.js y el sistema de diseño.
---

# Configuración de Marca y Tailwind

## Goal
Sincronizar las definiciones estéticas con la infraestructura técnica de Tailwind CSS.

## Instructions
1. **Tailwind Sync**: Verifica que los nuevos tokens de color o fuentes estén reflejados en [`tailwind.config.js`](file:///home/jorand/antigravityobuntu/tailwind.config.js).
2. **Build Process**:
   - Después de cualquier cambio, recuerda que es necesario ejecutar la compilación de CSS.
   - Script: `npm run build:css` (vía `package.json`).

## Constraints
- No modificar el archivo `tailwind.config.js` manualmente si el cambio puede automatizarse vía `brand_manager.py`.
- No alterar las rutas de `content` en el archivo de configuración de Tailwind.
