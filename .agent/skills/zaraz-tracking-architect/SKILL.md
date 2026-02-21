---
name: zaraz-tracking-architect
description: Arquitectura de Datos Blindados. Gestiona el tracking en el Edge (Zaraz) con sistemas de fallback dinámicos.
---

# 📊 Zaraz Tracking Architect - Jorge Aguirre Flores

## Propósito
Actuar como un **Data Architect** para blindar la captura de leads y el ROI publicitario. Esta skill asegura que el tracking basado en el Edge (Zaraz) nunca se pierda, incluso ante fallos de conexión o configuración.

## 🧠 Lógica de Datos: Resiliencia de Tracking
1.  **Panic-Debug**: Si el servidor de Zaraz no responde, analiza conflictos de reglas inmediatamente.
2.  **Fallback Dinámico**: Capacidad de inyectar scripts de respaldo en el cliente si la infraestructura de borde falla.
3.  **Validation First**: No se activa una nueva campaña sin verificar que los eventos de Zaraz disparan `HTTP 204` correctamente.

## 🛡️ Protocolo de Resiliencia (Zaraz)
Si `cloudflare-mcp` (zaraz) falla:
1.  **Verificación**: Consultar `get_zaraz_workflow`.
2.  **Aislamiento**: Identificar si el error es de configuración (JSON) o de red.
3.  **Continuidad**: Proponer un pixel de respaldo directo si Zaraz está caído.

## Instructions
1.  **Auditoría de Datos**: Verifica que todos los formularios estén vinculados a eventos de Zaraz.
2.  **Configuración Segura**: Usa `update_zaraz_config` con validación de esquema previa.
3.  **Monitoreo**: Asegura que el flujo de eventos sea constante.

## Métrica de Éxito
- 0% de pérdida de leads por fallos de tracking.
- Configuración de Zaraz validada y sin errores de esquema.
- Existencia de lógica de fallback verificada.
