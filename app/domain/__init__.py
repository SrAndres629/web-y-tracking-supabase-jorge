"""
🧠 Domain Layer - Corazón del negocio.

La capa de dominio contiene:
- Entidades: Objetos con identidad (Visitor, Lead, Event)
- Value Objects: Objetos inmutables sin identidad (Email, Phone, EventId)
- Repositorios (interfaces): Contratos para persistencia
- Servicios de Dominio: Lógica pura sin side effects
- Excepciones: Errores específicos del dominio

REGLA DE ORO: Esta capa NO tiene dependencias externas.
No importa: fastapi, psycopg2, redis, httpx, etc.
"""
