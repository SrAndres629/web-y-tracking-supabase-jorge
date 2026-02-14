"""
🎮 Application Layer - Casos de uso (CQRS).

Orquesta el flujo de datos entre:
- Interfaces (entrada): Routes, Webhooks
- Dominio: Entidades y reglas
- Infraestructura (salida): DB, Cache, APIs externas

Patrones:
- Command Handlers: Escrituras (crear, actualizar, eliminar)
- Query Handlers: Lecturas (buscar, listar, agregar)
- DTOs: Contratos de datos entre capas

REGLA: Los handlers no deben depender de FastAPI ni de detalles HTTP.
"""
