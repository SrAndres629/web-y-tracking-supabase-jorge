"""
🌐 Interface Layer - Adaptadores de entrada.

Expone la aplicación al mundo exterior:
- API REST: Routes de FastAPI
- Middleware: Seguridad, rate limiting, identity
- Webhooks: Receptores de eventos externos (QStash)

Responsabilidades:
1. Recibir requests HTTP
2. Validar/parsear input (DTOs)
3. Llamar a Application Layer (handlers)
4. Formatear responses

NO debe contener lógica de negocio.
"""
