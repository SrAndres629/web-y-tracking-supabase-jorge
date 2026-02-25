# app/__init__.py
# Jorge Aguirre Flores Web - Modular Backend Package

from .config import settings
from .infrastructure.persistence.database import db

__all__ = ["settings", "db"]
