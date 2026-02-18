# Protocolo de Ingeniería Autónoma v2.6 — Síntesis y Plan de Ejecución

## Síntesis: Lo Que Entiendo

### Estado Actual del Proyecto
El sitio **jorgeaguirreflores.com** es una plataforma de maquillaje permanente (microblading) en Santa Cruz, Bolivia. Stack: Python/Flask en Vercel, Tailwind CSS, Supabase, Meta CAPI tracking, Cloudflare.

### Lo Que Ya Se Logró (Esta Sesión)
1. **FOUC eliminado** — `app.min.css` render-blocking + critical CSS inline expandido
2. **Auditoría visual completa** — gallery, hero, process, testimonials, pricing, footer corregidos
3. **Auditoría estructural senior** — 4 de 5 errores críticos resueltos:
   - ✅ WCAG contraste (texto invisible → legible)
   - ✅ Overflow-X (anchuras fijas → viewport-relative)
   - ✅ Tipografía armónica (H1 48→36px mobile)
   - ✅ Ley de Fitts (touch targets ≥44px)
   - ⏳ CSS dedup (atoms vs input.css)

### Lo Que Pide El Usuario
Un protocolo de ingeniería autónoma donde Antigravity:
1. **Tenga memoria persistente** → `META_CONTEXT.json` con decisiones, deuda técnica, estado del negocio
2. **Tenga rigor matemático** → Scripts de validación para tracking/conversiones
3. **Use Stitch MCP** → Para diseño de UI profesional y prototipos

### Clarificación Técnica Sobre Stitch
Stitch MCP es una herramienta de **diseño de UI** (text-to-UI, generación de pantallas, variantes de diseño). Permite crear mockups de alta calidad que sirven como referencia visual. NO es un indexador de código ni un monitor de logs. Su valor real: generar pantallas de referencia para asegurar que el código HTML/CSS implementado coincida con un estándar visual profesional.

---

## Plan de Tareas

### Bloque A: Memoria Persistente (META_CONTEXT.json)
- [x] A1. Crear `scripts/generate_meta_context.py` — Script que escanea el proyecto y genera `META_CONTEXT.json`
- [x] A2. Generar `META_CONTEXT.json` inicial con: arquitectura, deuda técnica, estado de tracking, decisiones de diseño

### Bloque B: CSS Architecture Cleanup (Fix 5 pendiente)
- [x] B1. Auditar `atoms/*.css` vs `input.css @layer components` — identificar duplicados
- [x] B2. Eliminar CSS zombie y consolidar en `input.css`
- [x] B3. Rebuild CSS y verificar que no hay regresiones

### Bloque C: Stitch — Referencia Visual Mobile-First
- [x] C1. Crear proyecto Stitch "Jorge Aguirre — Mobile Landing"
- [x] C2. Generar pantalla hero mobile (390px) como referencia de diseño
- [x] C3. Generar pantalla de servicios/pricing mobile
- [x] C4. Comparar diseño Stitch vs implementación actual e identificar gaps

### Bloque D: Validación de Tracking (Rigor Matemático)
- [x] D1. Crear `tools/tracking_validator.py` — Script que valida integridad de eventos Meta CAPI
- [x] D2. Verificar que todos los CTAs del sitio llaman `handleConversion()` correctamente

### Bloque E: Despliegue Final
- [x] E1. Commit y deploy de todos los cambios
- [x] E2. Verificar Vercel deployment READY
- [x] E3. Purgar caché de Cloudflare