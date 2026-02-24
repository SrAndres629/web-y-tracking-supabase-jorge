"""
🗄️ Database Connection Management.

Serverless-optimized connection handling.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class Database:
    """
    Gestor de conexiones a base de datos.

    Soporta PostgreSQL (producción) y SQLite (desarrollo).
    Optimizado para serverless (sin connection pooling global).
    """

    def __init__(self, settings: Optional[Any] = None):
        self._settings = settings or get_settings()
        self._backend = self._detect_backend()

    def _detect_backend(self) -> str:
        """Detecta qué backend usar."""
        if self._settings.db.is_configured:
            return "postgres"

        # 🚨 FAIL FAST IN PRODUCTION
        # Si estamos en Vercel y no hay DB configurada, NO hacer fallback a SQLite.
        # Esto evita errores silenciosos o "invalid dsn" por mezcla de drivers.
        if os.getenv("VERCEL"):
            raise RuntimeError(
                "🔥 CRITICAL: DATABASE_URL is missing or invalid in Vercel. "
                "Cannot fall back to SQLite in a serverless environment."
            )

        return "sqlite"

    @property
    def backend(self) -> str:
        return self._backend

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator:
        """
        Context manager para conexiones.

        Yields:
            Connection object (psycopg2 o sqlite3)
        """
        if self._backend == "postgres":
            async with self._postgres_connection() as conn:
                yield conn
        else:
            async with self._sqlite_connection() as conn:
                yield conn

    @asynccontextmanager
    async def _postgres_connection(self) -> AsyncGenerator:
        """Conexión PostgreSQL."""
        import psycopg2
        import psycopg2.extras

        conn = None
        try:
            # Clean URL (strip all query params for psycopg2 compatibility)
            url = self._settings.db.url
            if url and "?" in url:
                url = url.split("?")[0]

            conn = psycopg2.connect(
                url,
                connect_timeout=5,
                sslmode="require",
            )
            yield conn
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @asynccontextmanager
    async def _sqlite_connection(self) -> AsyncGenerator:
        """Conexión SQLite (fallback)."""
        import sqlite3

        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "local.db"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# Singleton
db = Database()
