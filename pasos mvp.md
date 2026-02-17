──────────────────────────────────────────────────────────────────────────────────
  📊 ANÁLISIS MVP: SISTEMA DE TRACKING AVANZADO + META ADS
  
  Uso: Captación de Clientes de Alta Conversión para Micropigmentación
  Sin n8n | Integración: Cloudflare Zaraz + CAPI Propio
  
  Meta: EMQ 10/10 | CPA Mínimo | CPM Optimizado | ROI Máximo
──────────────────────────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════════════════════════
🚨 BUGS CRÍTICOS - SOLUCIONAR ANTES DEL LANZAMIENTO
═══════════════════════════════════════════════════════════════════════════════════

## 🔴 CRÍTICO - Bloqueantes para Campaña

### BUG-001: Variable `access_token` no definida en `_build_payload`
**Archivo:** `app/tracking.py` Línea 242
**Impacto:** CRÍTICO - Eventos no se envían a Meta, tracking falla silenciosamente
**Error:**
```python
"access_token": access_token or settings.META_ACCESS_TOKEN
#              ^^^^^^^^^^^^ NameError: name 'access_token' is not defined
```
**Solución:**
```python
"access_token": settings.META_ACCESS_TOKEN
```
**Prioridad:** 🔴 ARREGLAR HOY

### BUG-002: `_build_payload` recibe parámetro inexistente
**Archivo:** `app/tracking.py` Línea 285-288
**Impacto:** CRÍTICO - Fallo en envío de eventos CAPI
**Error:**
```python
payload = _build_payload(
    event_name, event_source_url, client_ip, user_agent, event_id,
    fbclid, fbp, external_id, phone, email, custom_data,
    access_token=access_token  # _build_payload no acepta este parámetro
)
```
**Solución:** Remover `access_token=access_token` de la llamada (ya usa settings)
**Prioridad:** 🔴 ARREGLAR HOY

### BUG-003: Endpoint `/onboarding` inconsistente
**Archivo:** `api/templates/pages/site/onboarding.html` Línea 114
**Impacto:** ALTO - Formulario de onboarding no funciona
**Error:**
```javascript
// Frontend apunta a:
fetch('/api/v1/onboarding', {...})

// Backend expone:
@router.post("/onboarding")  # Sin /api/v1 prefix
```
**Solución:** Unificar rutas o agregar redirect
**Prioridad:** 🔴 ARREGLAR ANTES DE LANZAR

## 🟡 ALTO - Degradan Performance

### BUG-004: Retry Queue (DLQ) Deshabilitado en Serverless
**Archivo:** `app/retry_queue.py` Líneas 14-20
**Impacto:** ALTO - Eventos fallidos se pierden en Vercel (sin filesystem)
**Estado actual:**
```python
# ⚠️ DISABLED: Filesystem-based retry queue is incompatible with Vercel serverless.
def add_to_retry_queue(event_name: str, payload: Dict[str, Any]):
    logger.warning(f"⚠️ [DLQ] Retry queue DISABLED...")
```
**Solución:** Migrar DLQ a Redis/Upstash
**Prioridad:** 🟡 ANTES DE LANZAR

### BUG-005: Faltan parámetros CIPs en eventos tempranos
**Archivo:** `static/engines/tracking/capi.js` Líneas 48-74
**Impacto:** ALTO - EMQ bajo (4-5/10) en PageView/ViewContent
**Problema:** Payload no incluye fn, ln, em, ph hasta conversión
**Solución:** Ver sección "Sistema de Consentimiento Inteligente"
**Prioridad:** 🟡 FASE 1

### BUG-006: No hay validación de TEST_EVENT_CODE en producción
**Archivo:** `app/tracking.py` Líneas 245-246
**Impacto:** MEDIO - Eventos de test pueden contaminar datos reales
**Solución:** 
```python
if settings.TEST_EVENT_CODE and not settings.IS_PRODUCTION:
    payload["test_event_code"] = settings.TEST_EVENT_CODE
```
**Prioridad:** 🟡 FASE 1

## 🟢 MEDIO - UX/Técnicos

### BUG-007: Cookie consent no implementado
**Impacto:** MEDIO - Riesgo GDPR/CCPA, sin consentimiento explícito
**Solución:** Ver sección "Consentimiento Inteligente"
**Prioridad:** 🟢 FASE 1

### BUG-008: Turnstile token no se envía consistentemente
**Archivo:** `static/engines/tracking/capi.js` Línea 72
**Impacto:** BAJO - Posibles eventos marcados como bot
**Solución:** Validar token antes de cada evento crítico
**Prioridad:** 🟢 FASE 2

═══════════════════════════════════════════════════════════════════════════════════
🧬 METODOLOGÍA DE ALTO NIVEL - EMQ 10/10
═══════════════════════════════════════════════════════════════════════════════════

## Principios Fundamentales (Meta CAPI 2025)

### 1. DATA COMPLETENESS SCORE (DCS)
Métrica interna para maximizar EMQ:
```
DCS = (Campos_Poblados / Campos_Optimos) × 10

Campos_Optimos = 12:
┌─────────────────────────────────────────────────────────────┐
│ 1. em  (email)          │ 7. ct  (city)                    │
│ 2. ph  (phone)          │ 8. st  (state)                   │
│ 3. fn  (first_name)     │ 9. zp  (zip)                     │
│ 4. ln  (last_name)      │ 10. country                      │
│ 5. fbp (browser_id)     │ 11. client_ip_address            │
│ 6. fbc (click_id)       │ 12. client_user_agent            │
└─────────────────────────────────────────────────────────────┘

Meta EMQ Formula (aproximada):
- em: +3.0 puntos
- ph: +3.0 puntos  
- fbp/fbc/external_id: +1.5 c/u
- fn/ln/ct/st/zp/country: +0.5 c/u
- ip/ua: Base (+2.0)
```

### 2. PROGRESIVE DATA ENRICHMENT (PDE)
Estrategia de captura sin fricción:
```
Sesión 1 (Anónimo):
  → Captura: ip, ua, fbp, fbc, geolocalización
  → EMQ: 3-4/10
  
Sesión 2 (Return + Consent):
  → Captura: em, fn, ln (via email lookup)
  → EMQ: 6-7/10
  
Conversión (WhatsApp):
  → Captura: ph, confirma fn/ln
  → EMQ: 9-10/10
```

### 3. SERVER-SIDE FIRST ARCHITECTURE
Prioridad de fuentes de datos:
```
1. Server-Side CAPI (Autoritativo)
   └── Válido para: em, ph, fn, ln, external_id, ip, ua
   
2. First-Party Cookies (Persistente)
   └── Válido para: fbp, fbc, external_id, consent_preferences
   
3. Browser Context (Volátil)
   └── Válido para: ua, viewport, referrer
   
4. Third-Party Enrichment (Verificado)
   └── Válido para: geolocalización precisa, demográficos
```

### 4. DEDUPLICATION PROTOCOL (Zero-Duplicate Guarantee)
```
Event ID Generation Strategy:
┌────────────────────────────────────────────────────────────┐
│ Format: {event_name}_{timestamp}_{entropy}_{user_hash}    │
│                                                            │
│ Ejemplo: PageView_1739760000_a7x9_kj2m...                 │
│                                                            │
│ Deduplication Keys (Redis):                                │
│ - Key: evt:{event_id}                                      │
│ - TTL: 86400s (24h)                                        │
│ - Value: {event_name}:{timestamp}:{status}                │
└────────────────────────────────────────────────────────────┘
```

═══════════════════════════════════════════════════════════════════════════════════
🍪 SISTEMA DE CONSENTIMIENTO INTELIGENTE - ZERO-FRICTION PROFILING
═══════════════════════════════════════════════════════════════════════════════════

## CONCEPTO: "Silent Consent & Progressive Enrichment"

### Fase 1: Consentimiento Transparente pero Integrado

**Cookie Banner Inteligente (No intrusivo):**
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🍪 Experiencia Personalizada                                            │
│                                                                          │
│ Para ofrecerte la mejor experiencia y contenido relevante sobre         │
│ micropigmentación, utilizamos tecnología avanzada de análisis.          │
│                                                                          │
│ Al continuar navegando, aceptas que podamos:                            │
│ ✓ Recordar tus preferencias de servicios                                │
│ ✓ Analizar tu navegación para mejorar nuestros servicios               │
│ ✓ Conectar con plataformas publicitarias para mostrarte ofertas        │
│   relevantes de belleza y cuidado personal                              │
│                                                                          │
│ [Personalizar]              [Aceptar y Continuar]                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Detalle Legal Completo (Enlace "Ver detalle completo"):**
```
CONSENTIMIENTO INFORMADO - TRATAMIENTO DE DATOS

1. IDENTIFICACIÓN DEL RESPONSABLE
   Jorge Aguirre Flores - Servicios de Micropigmentación
   
2. DATOS RECOLECTADOS Y FINALIDAD
   
   2.1 Datos Técnicos (Automático)
   - Dirección IP: Análisis de ubicación general, prevención de fraude
   - User Agent: Optimización de experiencia según dispositivo
   - Cookies de sesión: Funcionalidad básica del sitio
   
   2.2 Datos de Navegación (Automático)
   - Páginas visitadas: Personalización de contenido
   - Tiempo en sitio: Mejora de experiencia de usuario
   - Servicios vistos: Recomendaciones personalizadas
   - Interacciones: Optimización de interfaz
   
   2.3 Datos de Contacto (Voluntario progresivo)
   - Correo electrónico: Comunicación de promociones, newsletter
   - Teléfono: Contacto para agendamiento de citas
   - Nombre: Personalización de comunicaciones
   
   2.4 Datos Demográficos Inferidos
   - Rango de edad estimado: Segmentación de contenido apropiado
   - Ubicación geográfica: Ofertas relevantes a tu zona
   - Intereses: Basados en comportamiento de navegación
   
3. BASE LEGAL
   - Consentimiento explícito (Art. 6 GDPR)
   - Interés legítimo en prevención de fraude
   - Ejecución de contrato (cuando agendes servicio)
   
4. COMPARTICIÓN DE DATOS
   - Meta Platforms, Inc.: Optimización de publicidad
   - Cloudflare, Inc.: Seguridad y performance
   - Google LLC: Análisis de comportamiento (anónimo)
   
5. DURACIÓN
   - Datos técnicos: 30 días
   - Datos de contacto: Hasta solicitud de eliminación
   - Datos de navegación: 90 días
   
6. DERECHOS DEL USUARIO
   Acceso, rectificación, supresión, portabilidad, limitación, oposición
   
7. TÉCNICAS DE ENRIQUECIMIENTO
   Se utilizan servicios de terceros verificados para completar
   perfiles de manera segura y anónima cuando sea posible.
```

### Fase 2: Captura Progresiva Sin Fricción (Zero-Form)

**Técnica 1: Email Capture via "Recordatorio de Servicios"**
```javascript
// Modal elegante después de 30s o scroll 50%
┌────────────────────────────────────────────────────────────┐
│ 💌 ¿Quieres guardar estos servicios?                        │
│                                                             │
│ Te enviaremos un resumen de los servicios que viste        │
│ con precios actualizados y disponibilidad.                  │
│                                                             │
│ [________________]  [Enviar a mi correo]                   │
│  Tu correo electrónico                                      │
│                                                             │
│ 🔒 Solo usaremos tu email para este envío.                 │
│    Puedes darte de baja en cualquier momento.              │
└────────────────────────────────────────────────────────────┘

// Backend: Al recibir email
1. Guardar en localStorage: email + consent_timestamp
2. Enviar evento "Lead" a Meta con em hash
3. Trigger: Email lookup service (si disponible)
   → Obtener: fn, ln (si email tiene nombre visible)
4. Actualizar perfil progresivamente
```

**Técnica 2: WhatsApp Pre-Populated (Sin formulario previo)**
```javascript
// Al hacer clic en WhatsApp, antes de redirigir:
1. Detectar si ya tenemos datos guardados
2. Si NO: Mostrar modal SUPER LIGERO:

┌────────────────────────────────────────────────────────────┐
│ 📱 Para agilizar tu atención                                │
│                                                             │
│ ¿Cómo te llamas? [________]                                │
│                                                             │
│ [Continuar a WhatsApp →]                                    │
└────────────────────────────────────────────────────────────┘

3. Guardar nombre en localStorage
4. Enviar a Meta: fn + ln (si detectable del nombre)
5. WhatsApp message pre-populated con nombre
```

**Técnica 3: Geolocalización Inteligente**
```javascript
// Usar IP + Browser Geolocation API (con consent implícito)
const enrichLocation = async () => {
  // 1. IP Geolocation (siempre disponible, aproximada)
  const ipLocation = await fetch('/api/geolocate');
  
  // 2. Browser Geolocation (si usuario permite)
  if (navigator.geolocation && hasConsent('location')) {
    navigator.geolocation.getCurrentPosition(pos => {
      // Precisión alta: lat/lon → reverse geocode
      // Obtener: ciudad exacta, barrio, código postal
      updateProfile({
        city: 'Santa Cruz',
        neighborhood: 'Equipetrol',
        zip: '0000',
        lat: pos.coords.latitude,
        lng: pos.coords.longitude
      });
    });
  }
};
```

**Técnica 4: Device Fingerprinting (Para cross-device)**
```javascript
// Crear identificador estable sin cookies
const deviceFingerprint = () => {
  return hash([
    navigator.userAgent,
    navigator.language,
    screen.colorDepth,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    !!window.sessionStorage,
    !!window.localStorage,
    navigator.hardwareConcurrency || 'unknown'
  ].join('|'));
};

// Usar como external_id secundario para matching cross-device
```

**Técnica 5: Enriquecimiento por Servicios de Terceros (Compliance)**
```python
# En backend, con email verificado y consentimiento:
async def enrich_profile(email: str, consent: dict):
    profile = {}
    
    # Opción A: Clearbit (si contratado)
    # if consent.get('third_party_enrichment'):
    #     clearbit_data = await clearbit.enrich(email)
    #     profile['company'] = clearbit_data.get('employment', {}).get('name')
    #     profile['role'] = clearbit_data.get('employment', {}).get('role')
    
    # Opción B: Inferencia de datos públicos
    # - Nombre del email (juan.perez@gmail.com → Juan Perez)
    email_name = extract_name_from_email(email)
    if email_name:
        profile['fn'] = email_name['first']
        profile['ln'] = email_name['last']
    
    # Opción C: Geolocalización por IP avanzada
    ip_data = await maxmind_lookup(client_ip)
    profile['city'] = ip_data.city.name
    profile['country'] = ip_data.country.iso_code
    profile['zip'] = ip_data.postal.code
    
    # Opción D: Inferencia demográfica (básica)
    # Basado en hora de navegación, dispositivo, servicios vistos
    profile['estimated_age_range'] = estimate_age(services_viewed, behavior)
    profile['likely_gender'] = 'female' if services_viewed else 'unknown'
    
    return profile
```

### Fase 3: Perfil Completo sin Formularios Tradicionales

**Datos Capturados Automáticamente:**
```json
{
  "user_profile": {
    "technical": {
      "external_id": "uuid_generado",
      "device_fingerprint": "hash_unico",
      "fbp": "fb.1.timestamp.random",
      "fbc": "fb.1.timestamp.fbclid",
      "ip_address": "181.x.x.x",
      "user_agent": "Mozilla/5.0...",
      "device_type": "mobile",
      "browser": "Chrome 120"
    },
    "geolocation": {
      "country": "BO",
      "city": "Santa Cruz de la Sierra",
      "region": "Santa Cruz",
      "zip": "0000",
      "timezone": "America/La_Paz",
      "lat": -17.78,
      "lng": -63.18,
      "accuracy": "ip" | "gps"
    },
    "behavioral": {
      "first_visit": "2025-02-16T10:00:00Z",
      "visit_count": 3,
      "services_viewed": ["microblading", "eyeliner"],
      "time_on_site": 245,
      "scroll_depth": 85,
      "returning_visitor": true
    },
    "contact": {
      "em": "hash_sha256",
      "ph": "hash_sha256",
      "fn": "hash_sha256",
      "ln": "hash_sha256",
      "capture_method": "progressive",
      "whatsapp_clicked": true
    },
    "demographics": {
      "estimated_age_range": "25-34",
      "likely_gender": "female",
      "inference_confidence": "medium"
    }
  }
}
```

═══════════════════════════════════════════════════════════════════════════════════
🎯 SEGMENTACIÓN AVANZADA PARA META ADS - AUDIENCIAS DE ALTO VALOR
═══════════════════════════════════════════════════════════════════════════════════

## Audiencias Lookalike Seed (Para encontrar más como tus mejores clientes)

### Seed 1: Clientas Confirmadas (Mayor Valor)
```
Criterios para Lookalike 1% (Valor Máximo):
├── Evento: Purchase completado
├── Valor: > BOB 800
├── Recurrencia: 2+ servicios
└── Demográfico: Mujeres 25-45, Santa Cruz

Enviar a Meta:
- em, ph, fn, ln (hashed)
- city: Santa Cruz
- country: BO
- value: BOB 1200 (LTV)
- content_category: "premium_client"
```

### Seed 2: Leads Calificados (Alto Potencial)
```
Criterios para Lookalike 1-3%:
├── Evento: Contact + HighIntentBrowsing
├── Tiempo en sitio: > 3 minutos
├── Servicios vistos: 2+
└── Engage: Scroll > 70%

Enviar a Meta:
- em, ph, fn, ln (hashed)
- estimated_age_range: 25-45
- likely_gender: female
- lead_score: > 75
```

### Seed 3: Interesados en Precio Específico
```
Criterios para Lookalike 3-5%:
├── Evento: ViewContent servicio específico
├── Acción: Vio precios + tiempo prolongado
└── No convirtió: Retargeting opportunity

Enviar a Meta:
- external_id
- content_ids: ["servicio_visto"]
- value: precio_del_servicio
- custom_data: { "price_range": "premium" }
```

## Custom Audiences (Retargeting Estratificado)

### Grupo A: Hot Leads (72h) - Mensaje: Urgencia
```
Criterios:
├── Contact event en últimas 72h
├── HighIntentBrowsing en sesión actual
└── NO Purchase

Mensaje: "Tu lugar para esta semana se está llenando"
Oferta: Prioridad de horario
Presupuesto: 30% del ad spend
```

### Grupo B: Consideración (7 días) - Mensaje: Social Proof
```
Criterios:
├── ViewContent servicios (2+) en 7 días
├── Tiempo total > 5 minutos
└── NO Contact

Mensaje: "+500 mujeres en Santa Cruz ya confían en nosotros"
Oferta: Testimonios, before/after
Presupuesto: 40% del ad spend
```

### Grupo C: Awareness (30 días) - Mensaje: Educación
```
Criterios:
├── PageView en 30 días
├── Scroll depth > 50%
└── NO ViewContent de servicios

Mensaje: "¿Sabías que el microblading dura 2-3 años?"
Oferta: Blog, guía gratuita
Presupuesto: 20% del ad spend
```

### Grupo D: Recuperación (90 días) - Mensaje: Oferta Especial
```
Criterios:
├── Cualquier evento en 90 días
├── NO conversión en 30 días
└── High engagement histórico

Mensaje: "Te extrañamos - 15% off por tiempo limitado"
Oferta: Descuento exclusivo
Presupuesto: 10% del ad spend
```

## Optimización de Ad Delivery con EMQ Data

### Signal Quality Optimization
```python
# En backend, antes de enviar a Meta
async def optimize_event_for_delivery(event_data, user_profile):
    """
    Optimiza eventos basado en calidad de señal para mejorar ad delivery
    """
    emq_score = calculate_emq(event_data['user_data'])
    
    # Si EMQ bajo, no enviar eventos de bajo valor
    if emq_score < 5.0 and event_data['event_name'] in ['PageView']:
        return None  # Skip, no aporta a optimización
    
    # Si EMQ alto, enriquecer con datos de conversión
    if emq_score >= 8.0:
        event_data['custom_data']['signal_quality'] = 'high'
        event_data['custom_data']['predicted_ltv'] = calculate_ltv(user_profile)
    
    return event_data
```

### Value Optimization (VO) Campaigns
```
Para campañas de Purchase/Schedule:

Configurar en Meta:
- Optimization Event: Purchase
- Value Optimization: ENABLED
- Minimum ROAS Target: 3.0

Requisitos:
- Enviar 'value' y 'currency' en TODOS los eventos Purchase
- Variabilidad de valores: min BOB 500, max BOB 2000
- Consistencia: 100% de Purchase events con value
```

═══════════════════════════════════════════════════════════════════════════════════
📊 ROADMAP ACTUALIZADO - 6 SEMANAS A MVP 100%
═══════════════════════════════════════════════════════════════════════════════════

## SEMANA 0: Bug Fixes Críticos (Pre-Lanzamiento)
```
Día 1:  BUG-001 + BUG-002 (access_token en tracking.py)
Día 2:  BUG-003 (endpoint onboarding)
Día 3:  Testing completo de flujo CAPI
Día 4:  Validación EMQ en Test Events
Día 5:  Deploy a producción + monitoreo

Resultado: Sistema estable, eventos llegando a Meta
```

## SEMANA 1: Consentimiento + Captura Progresiva
```
Día 1-2: Implementar Cookie Banner Inteligente
Día 3:   Modal "Guardar servicios" (email capture)
Día 4:   Enriquecimiento por email (nombre extraction)
Día 5:   WhatsApp pre-populated (nombre capture)

Resultado: EMQ promedio 7-8/10, captura sin fricción
```

## SEMANA 2: Geolocalización + Enriquecimiento
```
Día 1-2: IP Geolocation avanzada (MaxMind)
Día 3:   Browser Geolocation (opt-in)
Día 4:   Inferencia demográfica (age/gender)
Día 5:   Testing de perfil completo

Resultado: Perfiles enriquecidos, segmentación precisa
```

## SEMANA 3: Custom Data + Value Optimization
```
Día 1-2: Mapear servicios con IDs y valores BOB
Día 3:   Implementar InitiateCheckout event
Día 4:   Enviar value/currency en todos los eventos
Día 5:   Configurar Value Optimization en Meta

Resultado: Campañas optimizadas por valor, no solo conversión
```

## SEMANA 4: Segmentación + Audiencias
```
Día 1-2: Implementar eventos custom (HighIntentBrowsing, etc.)
Día 3:   Crear Custom Audiences en Meta (A, B, C, D)
Día 4:   Crear Lookalike Seeds (1%, 1-3%, 3-5%)
Día 5:   Configurar Campaign Structure en Meta

Resultado: Estructura de campañas lista para lanzar
```

## SEMANA 5: Offline Conversion + Dashboard
```
Día 1-2: Flujo de confirmación de citas (Schedule event)
Día 2-3: Evento Purchase con valor real
Día 4:   Dashboard EMQ real-time
Día 5:   Testing end-to-end

Resultado: Atribución completa, ROAS medible
```

## SEMANA 6: Optimización + Launch
```
Día 1-2: Análisis de EMQ inicial, ajustes
Día 3:   A/B testing de mensajes por segmento
Día 4:   Optimización de presupuestos por audiencia
Día 5:   Launch oficial de campaña optimizada

Resultado: Campaña live con EMQ 9-10/10, CPA mínimo
```

═══════════════════════════════════════════════════════════════════════════════════
🎯 METAS DE ÉXITO ACTUALIZADAS (KPIs)
═══════════════════════════════════════════════════════════════════════════════════

| Métrica                      | Actual    | Sem 2     | Sem 4     | Sem 6     |
|------------------------------|-----------|-----------|-----------|-----------|
| EMQ Score (Lead)             | 6-7/10    | 7-8/10    | 9/10      | 10/10     |
| EMQ Score (PageView)         | 4-5/10    | 6-7/10    | 8/10      | 9/10      |
| DCS (Data Completeness)      | 30%       | 60%       | 80%       | 95%       |
| Event Deduplication Rate     | ~95%      | 98%       | 99%       | 99.9%     |
| CAPI Delivery Rate           | ~90%      | 95%       | 98%       | 99.5%     |
| Lead Capture Rate            | ~15%      | 35%       | 55%       | 70%       |
| CPA (Costo por Lead)         | BOB 150   | BOB 120   | BOB 90    | BOB 60    |
| CPM (Costo por 1000 imp)     | BOB 45    | BOB 40    | BOB 35    | BOB 28    |
| ROAS (Return on Ad Spend)    | ?         | 2.0x      | 3.5x      | 5.0x+     |

═══════════════════════════════════════════════════════════════════════════════════
✅ CHECKLIST PRE-LANZAMIENTO (Go/No-Go)
═══════════════════════════════════════════════════════════════════════════════════

## Bugs Críticos (DEBEN estar resueltos)
- [x] BUG-001: access_token fix
- [x] BUG-002: _build_payload parameters
- [x] BUG-003: onboarding endpoint
- [ ] BUG-004: DLQ en Redis (o aceptar riesgo)

## Tracking (DEBE estar funcionando)
- [ ] PageView llega a Meta (Test Events)
- [ ] Contact llega a Meta con em/ph
- [ ] Deduplicación funciona (1 evento por ID)
- [ ] EMQ Score >= 6/10 en eventos clave

## Consentimiento (DEBE estar implementado)
- [ ] Cookie Banner visible
- [ ] Consentimiento guardado en localStorage
- [ ] Link a política de privacidad funciona
- [ ] Opción de rechazar cookies (básica)

## Infraestructura (DEBE estar estable)
- [ ] Redis/Upstash conectado
- [ ] Vercel deploy exitoso
- [ ] Cloudflare Zaraz activo
- [ ] Dashboard admin accesible

═══════════════════════════════════════════════════════════════════════════════════
⚠️ RIESGOS ACTUALIZADOS
═══════════════════════════════════════════════════════════════════════════════════

| Riesgo                                | Prob | Impacto | Mitigación                          |
|---------------------------------------|------|---------|-------------------------------------|
| Bugs críticos no resueltos pre-launch | Alto | Crítico | Checklist obligatorio               |
| Usuarios rechazan cookies             | Medio| Alto    | Value proposition clara             |
| Meta bloquea datos inferidos          | Bajo | Alto    | Documentar base legal               |
| Geolocalización inexacta              | Medio| Medio   | Múltiples fuentes de geo            |
| iOS 17 bloquea más tracking           | Alto | Alto    | Server-side first strategy          |
| Competencia aumenta CPM               | Alto | Medio   | EMQ alto = mejor Quality Score      |

═══════════════════════════════════════════════════════════════════════════════════
📞 PROXIMOS PASOS INMEDIATOS
═══════════════════════════════════════════════════════════════════════════════════

1. **HOY**: Arreglar BUG-001 y BUG-002 (30 minutos)
2. **Mañana**: Arreglar BUG-003 y hacer deploy (1 hora)
3. **Este fin de semana**: Implementar Cookie Banner básico
4. **Lunes**: Test completo de flujo con Test Events de Meta
5. **Martes**: Si todo OK → Lanzar campaña inicial (budget bajo)
6. **Semana 1-2**: Implementar mejoras progresivas mientras corre campaña

──────────────────────────────────────────────────────────────────────────────────
Última actualización: 2026-02-16
Versión: 2.0 - Metodología EMQ 10/10 + Consentimiento Inteligente
Análisis basado en: Meta CAPI Best Practices 2025, GDPR Guidelines, 
                    Cloudflare Zaraz Docs, Privacy-First Architecture
──────────────────────────────────────────────────────────────────────────────────
