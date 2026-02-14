"""
⚙️ Infrastructure Configuration.

Centraliza toda la configuración de la aplicación.
Usa Pydantic Settings para validación y type safety.
"""

from app.infrastructure.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
