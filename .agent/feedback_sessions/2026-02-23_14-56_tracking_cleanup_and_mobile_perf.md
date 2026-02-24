---
date: "2026-02-23T00:56:31-04:00"
title: "Tracking Cleanup & Mobile Performance Optimization"
description: "Informe de aprendizajes sobre la refactorización de base.html, la eliminación de Rudderstack en favor de Zaraz, y la corrección de errores en tests de dependencias y scripts autónomos."
tags: [performance, tracking, architecture, debugging]
---

# Feedback Session: Tracking Cleanup & Mobile Performance

A continuación se detalla el informe de los problemas encontrados, las soluciones implementadas y los aprendizajes técnicos extraídos durante esta sesión.

## 1. Comportamiento Autónomo del Agente y Estética (UI)
- **Error:** El agente autónomo tenía "Autonomía Total" (mediante la skill `stitch-vibe-translator`), lo que provocó que introdujera modificaciones estéticas genéricas que rompían la identidad visual "Elite Digital" del proyecto sin pedir autorización.
- **Solución:** Se eliminó la skill `stitch-vibe-translator`. Se restauraron los archivos de diseño (Tailwind e inputs) desde un backup local. Se modificó el prompt principal introduciendo un sistema de validación obligatoria apoyado por un nuevo script `multi_agent_reviewer.py` y la skill `auditor-planes`.
- **Aprendizaje:** Otorgar autonomía total a los agentes para modificar el sistema de diseño es riesgoso sin barreras de calidad (Quality Gates). Un modelo de 2 pasos (Planeación -> Revisión Multi-Agente -> Ejecución) preserva la estabilidad del código y el branding.

## 2. Rendimiento en Dispositivos Móviles (Mobile Performance)
- **Error:** La interfaz cargaba con lentitud en móviles. El problema no recaía en el peso de las imágenes (que ya eran WebP optimizadas), sino en el **Render-Blocking JavaScript**. Inicializar motores pesados (GSAP Lenis, Google Identity, analíticas) de forma síncrona en `base.html` ahogaba el hilo principal (Main Thread).
- **Solución:** Se implementó una estrategia de carga diferida (Lazy Evaluation) utilizando `requestIdleCallback` o envoltorios `setTimeout`. Esto pospuso la evaluación de JS no crítico hasta que el navegador terminara de pintar (paint) el DOM inicial.
- **Aprendizaje:** En arquitecturas ricas en animaciones (GSAP/AOS), es estrictamente necesario separar el CSS/HTML crítico del JavaScript de hidratación y posponer este último para proteger el LCP (Largest Contentful Paint) en los Core Web Vitals móviles.

## 3. Arquitectura de Rastreo (Tracking Redundancy)
- **Error:** Existía una alta redundancia en el tracking. El sitio mantenía implementaciones activas tanto de `RudderStack` (en backend/FastAPI) como de fallbacks locales de Facebook Pixel (`window.fbq` en `pixel-bridge.js`), cuando la arquitectura ya había sido migrada a **Cloudflare Zaraz** en el Edge.
- **Solución:** Se reescribió `pixel-bridge.js` para que todo evento fluya de manera nativa y exclusiva por `window.zaraz.track()`. Backend: Se borró radicalmente el SDK y los servicios de Rudderstack (`rudderstack.py`, `tracker.py`) para aligerar la carga del servidor.
- **Aprendizaje:** Mantener puentes de rastreo obsoletos por "seguridad" contamina el Performance y el hilo de red. Cloudflare Zaraz es lo suficientemente robusto para inyectar todo nativamente desde el CDN.

## 4. Efectos Secundarios en Tests (Dependency Injection)
- **Error:** Al remover la carpeta de Rudderstack, la suite de pruebas automatizadas falló masivamente disparando 233 `ImportError` en Pytest.
- **Solución:** Se descubrió que la inyección de dependencias estaba fuertemente acoplada. Fue necesario extirpar las llamadas a `RudderStackTracker` desde la caché singleton en `dependencies.py`, las flags de settings dictaminadas en `settings.py`, los inyectores de salud en `health.py` y los mocks automatizados inyectados mediante `MonkeyPatch` en `conftest.py`.
- **Aprendizaje:** Al eliminar librerías core, no basta con borrar sus módulos. Hay que auditar contenedores de IoC (Resolución de Dependencias), configuraciones globales (Pydantic Settings) y los fixtures base de Pytest.

---

## Estructura de Datos (JSON Format)
Para integraciones algorítmicas, aquí está el resumen de aprendizajes estructurado en formato JSON:

```json
{
  "session": {
    "id": "tracking_cleanup_mobile_perf",
    "timestamp": "2026-02-23T00:56:31-04:00",
    "focus": ["architecture", "performance", "CI/CD"],
    "records": [
      {
        "issue": "AI aesthetic drifting due to over-autonomy",
        "fix": "Introduced auditor-planes skill & multi_agent_reviewer.py gateway.",
        "layer": "Agentic Architecture"
      },
      {
        "issue": "Poor mobile LCP due to synchronous JS engine loading",
        "fix": "Used requestIdleCallback to defer GSAP and Google Identity in base.html.",
        "layer": "Frontend UI / DOM"
      },
      {
        "issue": "Redundant tracking payloads crossing Edge and Server boundaries",
        "fix": "Migrated strictly to window.zaraz. Purged all RudderStack code and fbq failovers.",
        "layer": "Data/Tracking Architecture"
      },
      {
        "issue": "Suite crash (233 generic errors) post-library deletion",
        "fix": "Surgically extracted Rudderstack bindings from dependencies.py, config, and conftest.py.",
        "layer": "Backend & Test Suite"
      }
    ]
  }
}
```
