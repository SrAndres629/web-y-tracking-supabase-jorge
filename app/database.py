"""
🔧 Backwards-compatible shim for app.database.

Redirects imports to app.infrastructure.persistence.database
and provides legacy API functions expected by tests.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict

from app.infrastructure.persistence.database import Database, db

logger = logging.getLogger(__name__)

# ── Legacy re-exports ───────────────────────────────────────────
# The DDD Database class uses async context managers, but legacy tests
# expect synchronous helpers. We provide thin wrappers here.

_backend: str = db.backend

BACKEND: str = db.backend


def _get_db_config() -> Dict[str, str]:
    """Returns dialect-specific SQL fragments used by tests."""
    if db.backend == "postgres":
        return {
            "id_type_uuid": "UUID DEFAULT gen_random_uuid()",
            "status_type": "TEXT",
        }
    return {
        "id_type_uuid": "TEXT",
        "status_type": "TEXT",
    }


def check_connection() -> bool:
    """Smoke test for connectivity (synchronous)."""
    try:
        if db.backend == "postgres":
            import psycopg2

            settings = db._settings
            url = settings.db.url
            if url and "?" in url:
                url = url.split("?")[0]
            conn = psycopg2.connect(url, connect_timeout=3, sslmode="require")
            conn.close()
            return True
        else:
            import sqlite3

            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "database", "local.db"
            )
            conn = sqlite3.connect(db_path)
            conn.close()
            return True
    except Exception as e:
        logger.warning(f"check_connection failed: {e}")
        return False


@contextmanager
def get_cursor():
    """Synchronous cursor context manager for legacy test code."""
    if db.backend == "postgres":
        import psycopg2

        settings = db._settings
        url = settings.db.url
        if url and "?" in url:
            url = url.split("?")[0]
        conn = psycopg2.connect(url, connect_timeout=5, sslmode="require")
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    else:
        import sqlite3

        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "database", "local.db"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()


def get_db_connection():
    """Synchronous connection context manager (yields raw connection)."""
    return _get_raw_connection()


@contextmanager
def _get_raw_connection():
    if db.backend == "postgres":
        import psycopg2

        settings_obj = db._settings
        url = settings_obj.db.url
        if url and "?" in url:
            url = url.split("?")[0]
        conn = psycopg2.connect(url, connect_timeout=5, sslmode="require")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        import sqlite3

        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "database", "local.db"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def init_tables():
    """Delegate to the Database singleton."""
    db.init_tables()


__all__ = [
    "Database",
    "db",
    "BACKEND",
    "_backend",
    "_get_db_config",
    "check_connection",
    "get_cursor",
    "get_db_connection",
    "init_tables",
]
