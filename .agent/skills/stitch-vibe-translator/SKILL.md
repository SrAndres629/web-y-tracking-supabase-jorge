---
name: stitch-vibe-translator
description: Estética Infalible. Traduce visión visual a código premium usando Stitch, con validación en Sandbox.
---

# 🎨 Stitch Vibe Translator - Jorge Aguirre Flores

## Propósito
Actuar como un **Lead Frontend Developer** para transformar visiones estéticas en componentes de UI impecables. Esta skill utiliza **Stitch** para la generación de código, pero añade una capa de control de calidad para evitar errores de diseño.

## 🧠 Lógica de Diseño: Resiliencia Estética
1.  **Sandbox Validation**: Antes de integrar código de Stitch, se simula su renderizado para verificar el cumplimiento del grid de 8px.
2.  **Vibe Alignment**: Asegura que cada componente generado herede los tokens de la skill `marca` (dorados, fuentes, espaciados luxury).
3.  **Conservative Retries**: Si Stitch genera algo "creativo" que rompe el layout, se reintenta con parámetros más conservadores y guiados.

## 🛡️ Protocolo de Estética (Stitch)
Si `StitchMCP` genera código nulo o erróneo:
1.  **Detención**: No inyectar el código en los templates vivos.
2.  **Re-contextualización**: Limpiar el historial del modelo y re-enviar el prompt con especificaciones técnicas del grid.
3.  **Manual Fallback**: Proporcionar una versión base manual si la generación automática falla 3 veces.

## Instructions
1.  **Generación Curada**: Usa `generate_screen_from_text` con instrucciones de diseño específicas (Tokens).
2.  **Control de Calidad**: Verifica las sugerencias de `output_components` antes de aceptarlas.
3.  **Integración Premium**: Asegura que el componente generado no tenga clases Tailwind ad-hoc que contradigan el design system.

## Métrica de Éxito
- 100% de componentes alineados con el grid de 8px.
- Cero regresiones visuales tras inyecciones de código.
- Tasa de éxito de generación de primer intento elevada.
