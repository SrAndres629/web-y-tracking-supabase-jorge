"""
🔧 Infrastructure Layer - Implementaciones concretas.

Implementa los contratos (interfaces) definidos en:
- Domain (repositorios)
- Application (puertos)

Contiene todo el I/O:
- Persistencia: PostgreSQL, SQLite
- Caché: Redis, In-Memory
- APIs Externas: Meta CAPI, RudderStack, n8n
- Configuración: Settings, Logging

Esta capa PUEDE cambiar sin afectar el dominio.
"""
