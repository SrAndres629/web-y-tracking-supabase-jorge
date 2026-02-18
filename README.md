### 💎 Jorge Aguirre Flores - High-Performance Web & Tracking Core

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

## 📦 Arquitectura de Dependencias (Modularized)

Para maximizar la mantenibilidad y la velocidad de construcción, el sistema utiliza una estructura de dependencias segmentada en la carpeta `requirements/`:

*   **`00-core.txt`**: El motor base (FastAPI) + `beartype` para validación de tipos O(1) de alto rendimiento.
*   **`01-persistence.txt`**: Puente de datos. Integra **Supabase (Postgres)** y **Redis** (Dual-mode: Sync para tests, REST/Upstash para producción serverless).
*   **`02-tracking.txt`**: SDKs industriales para **Meta CAPI** y **RudderStack**.
*   **`03-platform.txt`**: Suite de Observabilidad Élite. Combina **Sentry**, **Structlog** (logs legibles por máquinas) y **Logfire** (trazabilidad profunda de Pydantic).
*   **`04-identity.txt`**: Seguridad y Verificación. Manejo de **OAuth (Google Auth)** y **JWT Processing**.
*   **`05-stability.txt`**: Capa de Resiliencia. Incluye `tenacity` (retries), `slowapi` (rate limiting), **HTMX** (UI reactiva) y **BeautifulSoup4** (Auditoría SEO en cada build).

---

## 🛠️ Stack Tecnológico (Deep Dive)

### 🐍 Backend: FastAPI & Pythonic Excellence
*   **Engine**: FastAPI (Async) para máximo rendimiento I/O.
*   **Validation & Perf**: Pydantic v2 + `beartype` para asegurar que el sistema sea un "Zero-Defect system" sin penalización de velocidad.
*   **Observability**: **Logfire** proporciona telemetría en tiempo real sobre el ciclo de vida de cada petición.

### 🗄️ Persistence & Distributed Cache
*   **Supabase**: Base de datos Postgres con gestión de identidades integrada.
*   **Upstash Redis**: Fundamental para la **Deduplicación de Eventos**. Evita el "Split-Brain" en el tracking de conversiones mediante un cache global distribuido.

### 🎨 Frontend: Premium Motion & UX
*   **HTMX**: Implementado para transiciones de UIX fluidas en dispositivos móviles sin el overhead de un framework JS pesado.
*   **GSAP & Lenis**: Animaciones y scroll de grado cinematográfico.
*   **SEO Monitoring**: Cada despliegue es auditado automáticamente por un motor basado en `bs4` para verificar la jerarquía semántica.

---

## 📂 Estructura del Proyecto

El proyecto sigue una estructura de **Clean Architecture / DDD** organizada en capas:

```bash
├── api/                   # Entrada Vercel & Templates
├── app/                   # Lógica central (Clean/DDD)
│   ├── application/       # Comandos, Handlers, DTOs
│   ├── core/              # Utilidades de bajo nivel
│   ├── domain/            # Entidades y Repositorios Port
│   ├── infrastructure/    # Adaptadores (Postgres, Redis, Meta)
│   └── interfaces/        # Rutas API, Middlewares
├── requirements/          # Dependencias segmentadas (Core, Infra, Stability)
├── scripts/               # Herramientas de soporte y legacy
├── tests/                 # QA Pipeline (L1-L6 Supervisor System)
├── git_sync.py            # Pipeline de despliegue automatizado
└── main.py                # Entrada para desarrollo local
```

---

## 🚀 Guía de Desarrollo

### Ejecución Local
1.  **Entorno**: `python -m venv venv` e inyectar `.env`.
2.  **Modular Deps**: `pip install -r requirements-dev.txt`.
3.  **Run**: `python main.py`.

### Pipeline "Iron Gate"
Para desplegar: `python git_sync.py "Commit message"`.
Este script bloquea el despliegue si falla la **Auditoría Diamante** (seguridad, tests L1-L5, integridad de assets y SEO).

---


---

## 📜 Licencia y Propiedad
Proyecto privado. Jorge Aguirre Flores - Web & Tracking Systems.
