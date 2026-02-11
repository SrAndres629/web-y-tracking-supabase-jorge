# 💎 Jorge Aguirre Flores - High-Performance Web & Tracking Core

Este es el motor central de la presencia digital de Jorge Aguirre Flores. Un sistema diseñado bajo el **Silicon Valley Standard** de rendimiento, utilizando una arquitectura híbrida Serverless para garantizar tiempos de respuesta ultra-rápidos (<100ms TTFB) y un tracking de conversiones de grado industrial.

---

## 🏛️ Arquitectura del Sistema (The Big Picture)

El sistema opera en una malla distribuida que prioriza la baja latencia y la integridad de los datos de tracking.

```mermaid
graph TD
    User([🌐 Usuario Final])
    CF{{"🛡️ Cloudflare (Edge)"}}
    Vercel["⚡ Vercel (FastAPI Serverless)"]
    Supa[("🗄️ Supabase (Postgres)") ]
    Redis[("🚀 Upstash (Redis)")]
    MetaAPI[("🔗 Meta Conversions API")]

    User -->|HTTPS/HTTP3| CF
    CF -->|Edge Cache / Zaraz| User
    CF -->|Protected Request| Vercel
    Vercel -->|Identity Capture| Redis
    Redis -->|Deduplication| Vercel
    Vercel -->|SQL Transaction (Port 6543)| Supa
    Vercel -->|Server-Side Event| MetaAPI
```

### Flujo de Datos
1.  **Ingreso**: El tráfico es filtrado en el Edge por **Cloudflare**, aplicando reglas de firewall y cache selectiva.
2.  **Cómputo**: Las peticiones llegan a **FastAPI** corriendo en **Vercel Functions**.
3.  **Persistencia**: Se utiliza **Supabase** con un Pooler de Transacciones (PgBouncer) para evitar el agotamiento de conexiones en entornos serverless.
4.  **Inteligencia de Capa**: **Upstash Redis** gestiona el Rate Limiting y la deduplicación de eventos de Meta en tiempo real.

---

## 🛠️ Stack Tecnológico (Deep Dive)

### 🐍 Backend: FastAPI & Pythonic Excellence
*   **Engine**: FastAPI (Async) para máximo rendimiento I/O.
*   **Validation**: Pydantic para esquemas de datos estrictos.
*   **Database Management**: `psycopg2` implementado con un patrón de conexión única por petición para optimizar el handshaking de TLS en PostgreSQL.
*   **Limiter & Cache**: Implementación nativa en `app/limiter.py` que consulta Upstash Redis para prevenir ataques de fuerza bruta y scraping sin penalizar a usuarios legítimos.

### 🎨 Frontend: Premium Motion & UX
*   **Jinja2 Templates**: Renderizado del lado del servidor (SSR) para SEO máximo.
*   **GSAP (GreenSock)**: Motor de animaciones de alto rendimiento para interacciones fluidas.
*   **Lenis Scroll**: Suavizado de scroll (Smooth Scroll) para una experiencia de navegación "premium".
*   **Asset Pipeline**: CSS puro y JS modular, servidos con compresión Brotli/Gzip desde el Edge.

### 📈 Tracking & Data: Diamond Standard
*   **Hybrid Tracking**: Sistema dual que combina el Meta Pixel (Browser) con la Meta Conversions API (Server) mediante `app/meta_capi.py`.
*   **Deduplication Core**: Uso de Redis para almacenar `event_id` y asegurar que Meta no cuente dos veces la misma conversión, mejorando la eficiencia de los Ads.
*   **Identity Middleware**: `app/middleware/identity.py` captura huellas digitales anónimas para mantener la atribución a lo largo de la sesión sin comprometer la privacidad.

---

## 📂 Estructura del Proyecto

El proyecto sigue una estructura de **Clean Architecture / DDD** organizada en capas:

```bash
├── api/                   # Adaptador Mangum para entrada Vercel
├── app/                   # Lógica central del sistema (organizada por capas Clean/DDD)
│   ├── application/       # Capa de Aplicación (Comandos, Consultas, DTOs)
│   ├── core/              # Capa Core (utilidades, Result types)
│   ├── domain/            # Capa de Dominio (Entidades, Value Objects)
│   ├── infrastructure/    # Capa de Infraestructura (repositorios, APIs externas)
│   └── interfaces/        # Capa de Interfaz (rutas API, middleware)
│       └── api/
│           └── routes/    # Endpoints de la API (admin, identity, seo, pages, tracking)
├── scripts/               # Automatización (Enriquecimiento de datos, Cloudflare)
├── tests/                 # Suite de QA (Unitarios, Integración, E2E)
├── git_sync.py            # Pipeline de despliegue "Iron Gate"
└── main.py                # Punto de entrada para ejecución local
```

---

## 🚀 Guía de Despliegue y Desarrollo

### Ejecución Local
1.  **Entorno**: Crear un `venv` y activar: `python -m venv venv`.
2.  **Dependencias**: `pip install -r requirements.txt`.
3.  **Variables**: Configurar `.env` con las credenciales de Supabase y Meta.
4.  **Run**: `python main.py` o `uvicorn main:app --reload`.

### The Iron Gate (Despliegue)
Para desplegar, utiliza exclusivamente:
```bash
python git_sync.py "Descripción del cambio"
```
Este script ejecutará la **Auditoría de Arquitectura Diamond**, bloqueando el despliegue si detecta:
*   Secretos hardcodeados o placeholders.
*   Funciones de más de 50 líneas sin `# noqa`.
*   Prints de debug en producción.
*   Warning de cualquier tipo en la suite de tests.

---

## 📜 Licencia y Propiedad
Proyecto privado. Jorge Aguirre Flores - Web & Tracking Systems.
