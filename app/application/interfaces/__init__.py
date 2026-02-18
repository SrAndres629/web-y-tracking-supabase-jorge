"""
🔌 Application Ports - Interfaces para infraestructura.

La capa de aplicación define estos puertos (interfaces).
La infraestructura los implementa.

Esto invierte la dependencia:
- Application NO depende de infraestructura
- Infraestructura depende de Application (implementa sus puertos)
"""

from app.application.interfaces.cache_port import ContentCachePort, DeduplicationPort
from app.application.interfaces.tracker_port import TrackerPort

__all__ = [
    "ContentCachePort",
    "DeduplicationPort",
    "TrackerPort",
]
