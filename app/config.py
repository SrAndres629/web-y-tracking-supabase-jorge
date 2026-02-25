"""
🔧 Backwards-compatible shim for app.config.

Redirects all imports to app.infrastructure.config.settings.
Tests and legacy code import `from app.config import settings`.
"""
from app.infrastructure.config.settings import settings, get_settings  # noqa: F401

__all__ = ["settings", "get_settings"]
