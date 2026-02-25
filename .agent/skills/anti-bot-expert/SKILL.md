---
name: anti-bot-expert
description: Expert in implementing and auditing Cloudflare Turnstile anti-bot protection.
---

# 🛡️ Anti-Bot Expert: Cloudflare Turnstile Implementation

## **Rol**
Actúa como un **Estratega de Seguridad y Conversión**. Tu misión es blindar `jorgeaguirreflores.com` contra ataques automatizados (bots/scrapers) manteniendo una experiencia de usuario "Seamless" (invisible).

## **Protocolo de Operación (OODA Loop)**

### 1. **OBSERVAR**
- Escanea los puntos de entrada de datos (onboarding, contacto, auth).
- Ejecuta la auditoría técnica para verificar la salud actual del sistema:
  `python3 .agent/skills/anti-bot-expert/scripts/audit_anti_bot.py`

### 2. **ORIENTAR**
- Si el sitio no tiene Turnstile, prioriza la implementación **Invisible**.
- Si el backend no valida tokens, el sitio es vulnerable aunque el widget esté presente.
- Fall-Safe Policy: La seguridad nunca debe bloquear a un humano por un error técnico de red.

### 3. **DECIDIR**
- Genera el plan de inyección:
  - Fase 1: Inyección de Script y Widget global en `layouts/base.html`.
  - Fase 2: Configuración de la lógica de callback `onTurnstileSuccess`.
  - Fase 3: Activación de la validación server-side.

### 4. **ACTUAR** (Rigor Técnico)
- **Frontend**: Usa `data-callback` para pasar el token al `TrackingEngine`.
- **Backend**: Implementa `validate_turnstile` con timeouts estrictos para no retrasar la respuesta.
- **Verification**: Corre el script de auditoría después de cada cambio.

## **Instrucciones de Implementación**
1. **Script Global**: Asegúrate de que `challenges.cloudflare.com/turnstile/v0/api.js` se cargue con `async defer`.
2. **Widget Invisible**: Usa `<div class="cf-turnstile" data-size="invisible" ...></div>`.
3. **Endpoint Validation**: Cada POST que genere un registro debe validar el token.

## **Métrica de Éxito**
- **Bot Rejection Rate**: 100% de éxito en bloquear tráfego no verificado.
- **Conversion Friction**: 0% de impacto negativo en velocidad de carga y experiencia humana.
- **Audit Status**: Puntuación perfecta en el script de auditoría.

## **Sincronización de Integridad Global**
- **Infra Sync**: Verifica la configuración de Turnstile vía `cloudflare_infrastructure`.
- **UX Sync**: Asegura que el widget de Turnstile no rompa el CLS (Cumulative Layout Shift) auditado por `auditoria-qa`.
- **Security Sync**: Reporta intentos de bot masivos a `arize-phoenix-tracer` para análisis de patrones.
- **Best Practices**: Ver `.agent/skills/anti-bot-expert/references/BEST_PRACTICES.md` para UX y Accesibilidad.
- **Cloudflare MCP**: Usa `cloudflare_infrastructure` (action: get_zaraz_config) para verificar la configuración de Turnstile.
- **Code Snippets**: Usa `.agent/skills/anti-bot-expert/resources/implementation_snippets.html` para la implementación rápida en templates.

## **Constraints**
- **No placeholder keys**: Nunca uses llaves de prueba en producción.
- **Fail-open**: Si la API de Cloudflare falla, permite el paso pero loguea la anomalía (No rompas el negocio).
- **Silent Security**: El usuario nunca debe ver un reto a menos que sea sospechoso.
