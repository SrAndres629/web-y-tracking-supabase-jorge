---
name: edge-mastery-ops
description: Infraestructura Resiliente (SRE). Optimiza el despliegue y la caché entre Cloudflare y Vercel con protocolos de auto-sanación.
---

# 🏗️ Edge Mastery Ops - Jorge Aguirre Flores

## Propósito
Actuar como un **Site Reliability Engineer (SRE)** para garantizar que la infraestructura que soporta el frontend sea estable, rápida y segura. Esta skill gobierna la relación entre el Borde (Cloudflare) y el Despliegue (Vercel).

## 🧠 Lógica de Infraestructura: Resiliencia SRE
1.  **Stop & Fix**: Si un MCP de infraestructura falla, la prioridad es restaurar la conexión antes de realizar cualquier cambio en el código.
2.  **Edge Optimization**: Gestión de Early Hints, purga de caché inteligente y seguridad de tokens.
3.  **Deployment Safety**: No se suben cambios si el Edge no está en estado "Healthy".

## 🛡️ Protocolo Circuit Breaker (MCP)
Si `cloudflare-mcp` o `my-vercel-mcp` devuelven errores:
1.  **Pausa**: Detener flujo de despliegue.
2.  **Diagnóstico**: Verificar `CLOUDFLARE_API_TOKEN` y estado de la zona.
3.  **Reparación**: Reintento exponencial y aviso de estado de red.

## Instructions
1.  **Auditoría de Infra**: Verifica el estado de los despliegues en Vercel y la configuración de caché en Cloudflare.
2.  **Circuit Breaker**: Ante cualquier error de herramienta, ejecuta `verify_token_permissions` mediante `cloudflare_master`.
3.  **Performance Boost**: Sincroniza optimizaciones de red (`performance_boost_sync`).

## Métrica de Éxito
- Tiempo de despliegue estable.
- 100% de éxito en purgas de caché y optimizaciones de borde.
- Inexistencia de errores en cadena por fallos de MCP.
