---
name: marca-colores
description: Sub-skill para gestionar la paleta de colores de la marca Jorge Aguirre. Úsala para consultar o modificar códigos hexadecimales de colores como luxury-gold, luxury-black, etc.
---

# Gestión de Colores de Marca

## Goal
Asegurar que cualquier cambio en la paleta de colores se realice de forma coherente en los archivos de tokens CSS y configuraciones de diseño.

## Instructions
1. **Verificar Token**: Identifica el nombre del token en [`colors.css`](file:///home/jorand/antigravityobuntu/static/design-system/tokens/colors.css).
2. **Consultar Guía**: Revisa la [Guía de Marca](file:///home/jorand/antigravityobuntu/.agent/skills/marca/references/BRAND_GUIDE.md) para asegurar que el nuevo color sea coherente con la visión de "Lujo Silencioso".
3. **Ejecutar Cambio**:
   - Usa el script de gestión: `python3 scripts/brand_manager.py color <token> <nuevo_valor>`
   - Esto actualizará automáticamente el CSS y sincronizará con Tailwind.

## Constraints
- Solo usar colores que mantengan el estándar de contraste WCAG AA para accesibilidad.
- Nunca modificar códigos de color sin usar el script `brand_manager.py` para evitar inconsistencias.
