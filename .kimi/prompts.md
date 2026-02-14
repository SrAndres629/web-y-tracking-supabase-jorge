# 📝 Prompts Preestablecidos - Kimi Max Power

## Comandos Rápidos con `kimi-max.ps1`

```powershell
# Análisis completo del proyecto
.\kimi-max.ps1 -Analyze

# Refactorización segura
.\kimi-max.ps1 -Refactor

# Debugging avanzado
.\kimi-max.ps1 -Debug

# Preparar para deploy
.\kimi-max.ps1 -Deploy

# Optimizar SEO
.\kimi-max.ps1 -Seo

# Auditar tracking
.\kimi-max.ps1 -Track

# Modo interactivo máximo poder
.\kimi-max.ps1

# Ejecutar prompt específico
.\kimi-max.ps1 -Prompt "Crea tests para el módulo de tracking"

# Iniciar Web UI
.\kimi-max.ps1 -Web -Port 8080

# Continuar sesión anterior
.\kimi-max.ps1 -Continue
```

---

## Prompts por Categoría

### 🏗️ Arquitectura & Código Limpio

```
Analiza el cumplimiento de Clean Architecture en app/. Identifica:
- Violaciones de la Regla de Dependencia
- Imports incorrectos entre capas
- Lógica de negocio en infraestructura
- Oportunidades para extraer value objects

Genera un plan de refactorización priorizado.
```

```
Revisa todos los repositorios en app/infrastructure/persistence/. 
Asegúrate que implementen correctamente los ABCs de domain/repositories/.
Identifica inconsistencias y propón mejoras.
```

```
Refactoriza app/interfaces/api/routes/ para extraer lógica de negocio
hacia los handlers en app/application/commands/ y app/application/queries/.
Las rutas solo deben orquestar.
```

### 🧪 Testing

```
Audita la cobertura de tests. Identifica:
- Handlers sin tests unitarios
- Rutas API sin tests de integración
- Mocks inadecuados
- Tests que no verifican comportamiento, solo ejecución

Crea los tests faltantes siguiendo el estilo existente.
```

```
Revisa tests/unit/test_handlers.py. Asegúrate que:
1. Usen repositorios InMemory
2. No dependan de infraestructura real
3. Prueben casos edge y errores
4. Sigan AAA (Arrange-Act-Assert)
```

### 🔒 Seguridad

```
Realiza una auditoría de seguridad:
1. Revisa manejo de secrets (.env, variables)
2. Valida sanitización de inputs en endpoints
3. Verifica rate limiting y protección contra abuse
4. Comprueba headers de seguridad
5. Identifica potenciales SQL injection
6. Revisa autenticación/autorización

Reporta hallazgos críticos primero.
```

### 🚀 Performance

```
Analiza el rendimiento del sistema de tracking:
1. Identifica N+1 queries en repositorios
2. Revisa eficiencia de deduplicación de eventos
3. Evalúa uso de cache
4. Optimiza llamadas a Meta CAPI (batching?)
5. Mejora tiempos de respuesta de endpoints

Prioriza cambios de mayor impacto.
```

### 📊 Tracking & Analytics

```
Verifica la integridad del tracking:
1. Lista todos los eventos trackeados
2. Valida estructura de eventos (fbc, fbp, external_id)
3. Comprueba deduplicación entre client-side y server-side
4. Testea eventos de Meta CAPI con test_event_code
5. Verifica flujo de datos a RudderStack

Documenta el estado de cada integración.
```

```
Implementa un nuevo evento de tracking:
Nombre: purchase_completed
Propiedades: value, currency, content_ids, content_type
Destinos: Meta CAPI (event_name: Purchase), RudderStack

Sigue el patrón existente en app/application/commands/track_event.py
```

### 🌐 SEO

```
Audita SEO técnico completo:
1. Revisa meta tags de todas las páginas en static/
2. Verifica sitemap.xml está actualizado
3. Comprueba robots.txt no bloquea contenido importante
4. Valida Open Graph y Twitter Cards
5. Revisa structured data (Schema.org)
6. Optimiza Core Web Vitals
7. Verifica canonical URLs

Crea un plan de mejoras priorizado.
```

```
Genera sitemap.xml dinámico que incluya:
- Todas las páginas estáticas
- URLs con prioridades basadas en importancia
- Fechas de última modificación
- Frecuencia de cambio apropiada

Sigue el estándar de sitemaps.org.
```

### 🗄️ Base de Datos

```
Revisa las migraciones en migrations/:
1. Valida que sean reversibles
2. Comprueba integridad de datos
3. Identifica migraciones potencialmente lentas
4. Verifica índices necesarios

Propón optimizaciones si es necesario.
```

```
Analiza el esquema de tracking_events:
1. Identifica columnas con alta cardinalidad
2. Propón índices para queries comunes
3. Evalúa particionamiento por fecha
4. Revisa retención de datos históricos
```

### 📚 Documentación

```
Actualiza AGENTS.md con los últimos cambios de arquitectura.
Asegúrate que:
1. La estructura de carpetas sea actual
2. Los ejemplos de código funcionen
3. Las convenciones estén claras
4. Los anti-patterns estén documentados
```

```
Genera documentación de API automáticamente:
- Extrae todos los endpoints de app/interfaces/api/routes/
- Documenta parámetros de entrada/salida
- Incluye ejemplos de requests/responses
- Lista códigos de error posibles

Formato: Markdown para docs/API.md
```

---

## Prompts Específicos del Proyecto

### Visitor & Identity

```
Revisa el sistema de identificación de visitantes:
1. Generación de fingerprint
2. Merge de perfiles
3. Asociación con leads
4. Resolución de identidad cross-device

Identifica edge cases y mejora robustez.
```

### Lead Management

```
Audita el flujo de captura de leads:
1. Formularios de captura
2. Validación de datos
3. Integración con CRM (si aplica)
4. Email de confirmación
5. Segmentación automática

Optimiza la conversión.
```

### Vercel Deployment

```
Verifica configuración para Vercel:
1. api/index.py está correcto
2. vercel.json tiene las reglas necesarias
3. Variables de entorno están documentadas
4. Cold start está optimizado
5. Errores 500 están manejados

Prepara checklist de deploy.
```

---

## Tips de Uso

### Uso Efectivo de MCP

```
Usa las herramientas MCP disponibles:
- filesystem: Lee/escribe archivos del proyecto
- fetch: Consulta documentación externa
- brave-search: Busca información actualizada
- sequential-thinking: Para problemas complejos
- playwright: Testea UI automáticamente
```

### Flujo de Trabajo Recomendado

1. **Antes de cambiar código**: Ejecuta `.\kimi-max.ps1 -Analyze`
2. **Durante desarrollo**: Usa modo interactivo con tests constantes
3. **Antes de commit**: Ejecuta `.\kimi-max.ps1 -Debug`
4. **Antes de deploy**: Ejecuta `.\kimi-max.ps1 -Deploy`

### Debugging con Kimi

```
Cuando algo falla:
1. "Muestra los logs de error de .kimi/logs/"
2. "Ejecuta los tests relacionados y muestra el output"
3. "Revisa el código de [archivo] línea [número]"
4. "Propón 3 posibles causas y verifica cada una"
```

---

*Actualizado: 2026-02-13*
*Versión: Max Power v1.0*
