---
date: "2026-02-25T12:30:00-04:00"
title: "Cross-System Integrity Audit: Redis Consolidation & Multi-Layer Cache Alignment"
description: "Deep audit de integridad entre Redis/Upstash, Cloudflare/Zaraz, Vercel CDN y Supabase. Consolidación de 6 conexiones Redis a 1 provider, unificación de dedup keys, corrección de Cache-Control y sincronización de eventos Zaraz."
tags: [redis, upstash, cloudflare, zaraz, vercel, cache, integrity, deduplication, DDD, MCP]
---

# Feedback Session: Cross-System Integrity Audit & Redis Consolidation

## 1. Arquitectura de Pensamiento y Trabajo Agéntico

- **Contexto:** El sistema había crecido orgánicamente con múltiples módulos (tracking, cache, dedup, DLQ, rate limiting) que creaban sus propias conexiones Redis de forma independiente. Cada módulo era funcional en aislamiento, pero juntos generaban inconsistencias silenciosas — especialmente en deduplicación de eventos donde prefijos de key incompatibles (`evt:` vs `dedup:`) causaban que el mismo evento pudiera pasar como "nuevo" dependiendo de qué módulo lo evaluara.

- **Desafío Agéntico:** La auditoría requirió un cambio de mentalidad: pasar de "¿funciona cada módulo?" a "¿son coherentes entre sí?". El agente tuvo que cruzar información de:
  - Código Python (6 archivos con Redis directo)
  - Cloudflare API real (via `cloudflare-mcp` → `get_zaraz_config`)
  - Vercel CDN headers (via `vercel.json` + middleware)
  - Supabase schema (vía `supabase-mcp-server`)
  - Sonatype auditoría de dependencias

  **Fallo agéntico identificado**: El intento de actualizar Zaraz config completa via `cloudflare-mcp` → `update_zaraz_config` falló 2 veces (1× validation error por `zarazVersion`, 1× timeout 504). La config era demasiado grande para una sola llamada REST. Lección: para configs complejas de Zaraz, usar el dashboard o dividir la actualización en chunks.

- **Solución/Aprendizaje:** 
  - **Patrón "Provider Singleton"**: Crear un módulo centralizado que actúa como Single Source of Truth para conexiones externas. Todos los consumidores importan el provider, nunca el SDK directamente.
  - **Auditoría con MCPs cruzados**: Usar los MCPs no solo para verificar estado individual sino para cruzar datos entre sistemas (ej: eventos en Zaraz config vs eventos en backend Python).
  - **Grep como validador**: `grep -r "from upstash_redis"` como test de regresión para confirmar que ningún módulo crea conexiones propias.

## 2. Desarrollo y Arquitectura de Software

- **Problema Técnico:** 
  - **6 singletons Redis** independientes: `cache.py`, `deduplication_service.py`, `retry_queue.py`, `redis_cache.py`, `rate_limiter_events.py`, `diagnostics.py`
  - **3 implementaciones de deduplicación** con key prefixes incompatibles → dedup silenciosamente rota
  - **Cache-Control conflicto 4 capas**: `vercel.json` (1 año) → `middleware/cache.py` (30 días override) → `pages.py` (1 hora) → `early_hints.py` (5 min fallback)
  - **`pipeline()` en rate_limiter**: Upstash REST no soporta Redis `pipeline()` → crash si se inyecta Redis
  - **Zaraz ↔ Backend desalineados**: 3 eventos backend (`Purchase`, `AddToCart`, `ViewContent`) sin triggers en Zaraz

- **Implementación:**
  1. Creado `app/infrastructure/cache/redis_provider.py` — provider lazy-init con sync + async clients
  2. Reescrito `deduplication_service.py` → usa provider, mantiene key prefix `evt:`
  3. Reescrito `redis_cache.py` (DDD port) → usa provider, cambió prefix `dedup:` → `evt:`
  4. Reescrito `retry_queue.py` → property-based access al provider
  5. Actualizado `rate_limiter_events.py` → auto-inject provider + `pipeline()` → `incr()` + `expire()` individuales
  6. Reescrito `cache.py` → thin wrapper sobre provider, eliminó visitor cache duplicado
  7. Actualizado `diagnostics.py` → `redis_provider.health_check()`
  8. Corregido `middleware/cache.py` → solo maneja HTML dinámico, no sobreescribe vercel.json
  9. Corregido `services/__init__.py` → QStash URL desde `settings.external.qstash_url`
  
  **MCPs utilizados**: `cloudflare-mcp` (zone listing, Zaraz config read/write), `supabase-mcp-server` (schema verification), `sonatype-guide` (dependency audit)

- **Aprendizaje Técnico:**
  - **Upstash REST ≠ Redis nativo**: `pipeline()`, `blpop()`, y otros comandos blocking no funcionan con Upstash REST. Siempre verificar compatibilidad.
  - **CDN Cache hierarchy**: Vercel procesa headers en orden `Vercel-CDN-Cache-Control` > `CDN-Cache-Control` > `Cache-Control`. El middleware de app siempre ejecuta DESPUÉS de vercel.json, así que puede sobreescribir los headers de CDN.
  - **Zaraz config updates**: La API de Cloudflare para Zaraz es sensible al campo `zarazVersion` — debe omitirse en updates (lo gestiona Cloudflare internamente). Configs grandes pueden causar 504 timeout.
  - **Key prefix consistency**: En sistemas con múltiples dedup layers, los prefijos de key DEBEN ser idénticos para que una verificación en un módulo sea visible en otro.

## 3. Objetivos y Tareas Trascendentales

- [x] **C2: Redis Provider único** — De 6 conexiones a 1. Impacto: menos latencia, estado consistente, menos costo Upstash
- [x] **C3: Dedup keys unificadas** — Prefix `evt:` universal. Impacto: deduplicación confiable cross-module
- [x] **H2: Cache-Control corregido** — Eliminado override de 1yr→30d. Impacto: mejor cache hit ratio en CDN
- [x] **H3: Pipeline API fix** — Upstash REST compatible. Impacto: rate limiter funcional con Redis
- [x] **M1+M2: Cache consolidado** — Eliminado visitor cache duplicado. Impacto: identity resolution consistente
- [x] **M3: QStash URL configurable** — Impacto: multiambiente sin hardcode
- [ ] **H1: Zaraz event sync** — Pendiente manual via dashboard (API timeout)
- [ ] **L2: Remover testKey** — `TEST88535` aún en Zaraz config

---

## Estructura de Datos (JSON Format)

```json
{
  "session": {
    "id": "2026-02-25_12-30_cross-system-integrity-redis-consolidation",
    "timestamp": "2026-02-25T12:30:00-04:00",
    "focus": ["redis", "integrity", "cache", "zaraz", "deduplication"],
    "records": [
      {
        "issue": "6 independent Redis/Upstash connections creating separate singletons across app modules",
        "fix": "Created redis_provider.py — single lazy-init provider with sync+async clients. All 5 consumers migrated.",
        "layer": "Backend"
      },
      {
        "issue": "3 deduplication implementations with conflicting key prefixes (evt: vs dedup:) causing silent dedup failures",
        "fix": "Unified all implementations to use evt:{event_id} prefix. Consolidated to 2 implementations (service + DDD port) sharing same keys.",
        "layer": "Data"
      },
      {
        "issue": "Cache-Control middleware overwriting vercel.json's 1-year immutable cache to 30 days for static assets",
        "fix": "Removed static asset handling from middleware — only handles dynamic HTML pages now. vercel.json controls CDN cache.",
        "layer": "Backend"
      },
      {
        "issue": "rate_limiter_events.py using pipeline() which is incompatible with Upstash REST API",
        "fix": "Replaced pipeline() with individual incr() + expire() calls. Auto-injected redis_provider as default client.",
        "layer": "Backend"
      },
      {
        "issue": "Zaraz config missing Purchase, AddToCart, ViewContent triggers that backend sends via CAPI",
        "fix": "Attempted via cloudflare-mcp but API timed out. Documented for manual update via Cloudflare Dashboard.",
        "layer": "Data"
      },
      {
        "issue": "QStash base URL hardcoded in services/__init__.py instead of using settings",
        "fix": "Replaced with settings.external.qstash_url with fallback to default Upstash endpoint.",
        "layer": "Backend"
      },
      {
        "issue": "Cloudflare MCP update_zaraz_config fails with zarazVersion in payload and times out on large configs",
        "fix": "Learned: omit zarazVersion from updates (CF manages it). Large configs need chunked updates or dashboard.",
        "layer": "Agentic Architecture"
      }
    ]
  }
}
```
