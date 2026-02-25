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

    def init_tables(self):
        """Inicializa las tablas si no existen (Sincrónico para arranque)."""
        logger.info(f"🛠️ Initializing tables for backend: {self._backend}")

        queries = [
            """
            CREATE TABLE IF NOT EXISTS visitors (
                external_id TEXT PRIMARY KEY,
                fbclid TEXT,
                client_ip TEXT,
                user_agent TEXT,
                source TEXT,
                email TEXT,
                phone TEXT,
                first_name TEXT,
                last_name TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT,
                external_id TEXT,
                fbclid TEXT,
                service_interest TEXT,
                status TEXT DEFAULT 'new',
                score FLOAT DEFAULT 0,
                utm_source TEXT,
                utm_campaign TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                external_id TEXT,
                source_url TEXT,
                custom_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                company TEXT,
                meta_pixel_id TEXT,
                meta_access_token TEXT,
                plan TEXT DEFAULT 'starter',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id),
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS emq_scores (
                id SERIAL PRIMARY KEY,
                client_id TEXT,
                event_name TEXT NOT NULL,
                score FLOAT NOT NULL,
                payload_size INTEGER,
                has_pii BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        if self._backend == "sqlite":
            # Adjust PostgreSQL syntax to SQLite
            queries = [
                q.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                .replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                .replace("ON CONFLICT", "-- ON CONFLICT")  # Simple fix for init
                for q in queries
            ]

        try:
            if self._backend == "postgres":
                import psycopg2

                url = self._settings.db.url
                if url and "?" in url:
                    url = url.split("?")[0]

                conn = psycopg2.connect(url, sslmode="require")
                cur = conn.cursor()
                for q in queries:
                    cur.execute(q)
                conn.commit()
                cur.close()
                conn.close()
            else:
                import sqlite3

                db_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "database",
                    "local.db",
                )
                conn = sqlite3.connect(db_path)
                for q in queries:
                    conn.execute(q)
                conn.commit()
                conn.close()
            logger.info("✅ Database tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database tables: {e}")


# Singleton
db = Database()
