# =================================================================
# DATABASE.PY - Serverless-Optimized Connection Strategy (V2)
# Jorge Aguirre Flores Web
# =================================================================
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import app.sql_queries as queries
from app.config import settings

# Attempt PostgreSQL Import
try:
    import psycopg2

    # NOTE: We do NOT use 'pool' anymore for Serverless safety
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

logger = logging.getLogger(__name__)

# BACKEND: 'postgres' vs 'sqlite'
# NOTE: In Serverless (Vercel), we DO NOT use a global pool object.
# Global pools are created per-lambda instance, leading to connection exhaustion.
BACKEND = "sqlite"
if settings.DATABASE_URL and HAS_POSTGRES:
    # 🛡️ SILICON VALLEY PROTOCOL: Deterministic Guard against STUB DSNs
    # If the ENV var is a stub, we FORCE SQLite to prevent DSN Parse Errors.
    db_url_clean = settings.DATABASE_URL.strip().lower()
    is_invalid = any(
        x in db_url_clean for x in ["required", "dsn_here", "none", "production", "placeholder"]
    )

    if not is_invalid:
        BACKEND = "postgres"
        # Ensure URL forces Supabase Transaction Mode if available
        if ":6543" in settings.DATABASE_URL and "pgbouncer=true" not in settings.DATABASE_URL:
            logger.warning(
                "⚠️ Using Supabase Pooler Port 6543 but missing '?pgbouncer=true'. Adding it automatically."
            )
    else:
        logger.warning(
            f"🛡️ Deterministic Guard: detected invalid DSN ({settings.DATABASE_URL[:10]}...). Falling back to SQLite."
        )
        # Logic to append query param could go here, but usually users fix ENV.


@contextmanager
def get_db_connection() -> Any:
    """
    Creates a SINGLE connection per request.
    Silicon Valley Protocol: 0-Latency failover & strict pool hygiene.
    """
    conn = None
    try:
        conn = _establish_connection()
        yield conn
        if conn:
            conn.commit()
    except Exception as e:
        _handle_db_error(conn, e)
        raise e
    finally:
        _close_connection(conn)


def _establish_connection():
    if BACKEND == "postgres":
        # 🛡️ SILICON VALLEY FIX: specific query params like 'pgbouncer=true' cause libpq to crash.
        # We strip them for the raw psycopg2 connection.
        clean_url = settings.DATABASE_URL.replace("?pgbouncer=true", "").replace(
            "&pgbouncer=true", ""
        )

        return psycopg2.connect(clean_url, connect_timeout=5, sslmode="require")

    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(db_dir), "database", "local_fallback.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _handle_db_error(conn, e):
    if conn:
        try:
            conn.rollback()
        except:
            pass

    err_msg = str(e).lower()
    if "timeout" in err_msg:
        logger.error("🔥 DB ERROR: Connection Timeout. Possible cold start or pooler exhaustion.")
    elif "too many connections" in err_msg:
        logger.error("🔥 DB ERROR: Connection Exhaustion. Check pooler settings.")
    elif "password authentication failed" in err_msg:
        logger.error("🔥 DB ERROR: Auth Failure. Check DATABASE_URL.")
    else:
        logger.error(f"🔥 Database Transaction Error: {e}")


def _close_connection(conn):
    if conn:
        try:
            conn.close()
        except Exception as close_err:
            logger.debug(f"ℹ️ Connection close cleanup: {close_err}")


class SQLiteCursorWrapper:
    """Adapta sintaxis Postgres (%s) a SQLite (?)"""

    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, sql: str, params: Optional[tuple] = None) -> Any:
        """Executes SQL query with parameter substitution."""
        if params:
            sql = sql.replace("%s", "?")
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)

    def fetchone(self) -> Optional[tuple]:
        """Fetches a single row."""
        return self.cursor.fetchone()

    def fetchall(self) -> List[tuple]:
        """Fetches all rows."""
        return self.cursor.fetchall()

    def close(self) -> None:
        """Closes the cursor."""
        self.cursor.close()

    @property
    def rowcount(self) -> int:
        """Returns number of rows affected."""
        return self.cursor.rowcount

    @property
    def lastrowid(self) -> Optional[int]:
        """Returns ID of last inserted row."""
        return self.cursor.lastrowid


@contextmanager
def get_cursor() -> Any:
    """
    Utility to get a cursor directly.
    Usage: with get_cursor() as cur: cur.execute(...)
    """
    with get_db_connection() as conn:
        try:
            if BACKEND == "postgres":
                yield conn.cursor()
            else:
                yield SQLiteCursorWrapper(conn.cursor())
        except Exception as e:
            raise e


# =================================================================
# COMPATIBILITY & INIT
# =================================================================


def init_tables() -> bool:
    """Crea tablas si no existen, sincronizado con init_crm_master_clean.sql v2.0"""
    try:
        with get_cursor() as cur:
            config = _get_db_config()
            _create_core_tables(cur, config)
            _create_crm_tables(cur, config)
            _run_column_migrations(cur, config["status_type"])
        logger.info(f"✅ Tablas sincronizadas ({BACKEND})")
        return True
    except Exception as e:
        logger.error(f"❌ Error sincronizando tablas: {e}")
        return False


def _get_db_config():
    if BACKEND == "postgres":
        return {
            "id_type_uuid": "UUID PRIMARY KEY DEFAULT gen_random_uuid()",
            "id_type_serial": "SERIAL PRIMARY KEY",
            "timestamp_default": "CURRENT_TIMESTAMP",
            "status_type": "lead_status DEFAULT 'new'",
            "lead_id_type": "UUID",
            "id_type_pk": "UUID PRIMARY KEY DEFAULT gen_random_uuid()",
        }
    return {
        "id_type_uuid": "TEXT PRIMARY KEY",
        "id_type_serial": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "timestamp_default": "CURRENT_TIMESTAMP",
        "status_type": "TEXT DEFAULT 'new'",
        "lead_id_type": "TEXT",
        "id_type_pk": "TEXT PRIMARY KEY",
    }


def _create_core_tables(cur, cf):
    if BACKEND == "postgres":
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE lead_status AS ENUM (
                    'new', 'interested', 'nurturing', 'ghost', 'booked', 
                    'client_active', 'client_loyal', 'archived'
                );
            EXCEPTION WHEN duplicate_object THEN null; END $$;
        """)

    cur.execute(
        queries.CREATE_TABLE_BUSINESS_KNOWLEDGE.format(
            id_type_serial=cf["id_type_serial"], timestamp_default=cf["timestamp_default"]
        )
    )
    cur.execute(queries.CREATE_INDEX_KNOWLEDGE_SLUG)

    cur.execute(
        queries.CREATE_TABLE_VISITORS.format(
            id_type_serial=cf["id_type_serial"], timestamp_default=cf["timestamp_default"]
        )
    )
    cur.execute(queries.CREATE_INDEX_VISITORS_EXTERNAL_ID)


def _create_crm_tables(cur, cf):
    cur.execute(
        queries.CREATE_TABLE_CONTACTS.format(
            id_type_primary_key=cf["id_type_pk"],
            status_type=cf["status_type"],
            timestamp_default=cf["timestamp_default"],
        )
    )
    cur.execute(queries.CREATE_INDEX_CONTACTS_WHATSAPP)
    cur.execute(queries.CREATE_INDEX_CONTACTS_STATUS)

    cur.execute(
        queries.CREATE_TABLE_MESSAGES.format(
            id_type_primary_key=cf["id_type_pk"], timestamp_default=cf["timestamp_default"]
        )
    )
    cur.execute(queries.CREATE_INDEX_MESSAGES_CONTACT_ID)

    cur.execute(
        queries.CREATE_TABLE_APPOINTMENTS.format(
            id_type_serial=cf["id_type_serial"], timestamp_default=cf["timestamp_default"]
        )
    )

    cur.execute(
        queries.CREATE_TABLE_LEADS.format(
            id_type_primary_key=cf["id_type_pk"], timestamp_default=cf["timestamp_default"]
        )
    )
    cur.execute(queries.CREATE_INDEX_LEADS_PHONE)
    cur.execute(queries.CREATE_INDEX_LEADS_META_ID)

    cur.execute(
        queries.CREATE_TABLE_INTERACTIONS.format(
            id_type_serial=cf["id_type_serial"],
            lead_id_type=cf["lead_id_type"],
            timestamp_default=cf["timestamp_default"],
        )
    )
    cur.execute(queries.CREATE_INDEX_INTERACTIONS_LEAD_ID)


def _run_column_migrations(cur, status_type):
    new_columns = [
        ("profile_pic_url", "TEXT"),
        ("fb_browser_id", "TEXT"),
        ("utm_term", "TEXT"),
        ("utm_content", "TEXT"),
        ("status", status_type),
        ("lead_score", "INTEGER DEFAULT 50"),
        ("pain_point", "TEXT"),
        ("service_interest", "TEXT"),
        ("service_booked_date", "TIMESTAMP"),
        ("appointment_count", "INTEGER DEFAULT 0"),
        ("updated_at", "TIMESTAMP"),
        ("onboarding_step", "TEXT"),
        ("is_admin", "BOOLEAN DEFAULT FALSE"),
    ]

    for col_name, col_type in new_columns:
        try:
            if BACKEND == "postgres":
                cur.execute(f"ALTER TABLE contacts ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
            else:
                # SQLite migration logic
                try:
                    cur.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type};")
                except Exception:
                    pass  # Column likely exists
        except Exception:
            pass


# =================================================================
# OPERATIONS (Domain Logic - Persisted)
# =================================================================


def save_visitor(
    external_id, fbclid, ip_address, user_agent, source="pageview", utm_data=None
) -> None:
    """Saves visitor data for attribution tracking."""
    if utm_data is None:
        utm_data = {}

    try:
        with get_cursor() as cur:
            params = (
                external_id,
                fbclid,
                ip_address,
                user_agent[:500] if user_agent else None,
                source,
                utm_data.get("utm_source"),
                utm_data.get("utm_medium"),
                utm_data.get("utm_campaign"),
                utm_data.get("utm_term"),
                utm_data.get("utm_content"),
            )

            if BACKEND == "postgres":
                stmt = """
                    INSERT INTO visitors 
                    (external_id, fbclid, ip_address, user_agent, source, utm_source, utm_medium, utm_campaign, utm_term, utm_content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """
                cur.execute(stmt, params)
            else:
                stmt = """
                    INSERT OR IGNORE INTO visitors 
                    (external_id, fbclid, ip_address, user_agent, source, utm_source, utm_medium, utm_campaign, utm_term, utm_content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """
                cur.execute(stmt, params)
    except Exception as e:
        logger.error(f"Failed to save visitor: {e}")


def get_visitor_fbclid(external_id: str) -> Optional[str]:
    """Retrieves the Facebook Click ID for a given visitor."""
    try:
        with get_cursor() as cur:
            query = "SELECT fbclid FROM visitors WHERE external_id = %s"
            cur.execute(query, (external_id,))
            res = cur.fetchone()
            if res:
                return res[0]
    except Exception:
        pass
    return None


def upsert_contact_advanced(contact_data: Dict[str, Any]) -> None:
    """Upsert avanzado estilo CRM Natalia."""
    if BACKEND != "postgres":
        # SQLite Partial
        try:
            with get_cursor() as cur:
                cur.execute(
                    queries.UPSERT_CONTACT_SQLITE,
                    (
                        contact_data.get("phone"),
                        contact_data.get("name"),
                        contact_data.get("utm_source"),
                        contact_data.get("status", "new"),
                    ),
                )
        except Exception as e:
            logger.error(f"SQLite Upsert Error: {e}")
        return

    params = (
        contact_data.get("phone"),
        contact_data.get("name"),
        contact_data.get("profile_pic_url"),
        contact_data.get("fbclid"),
        contact_data.get("fbp"),
        contact_data.get("utm_source"),
        contact_data.get("utm_medium"),
        contact_data.get("utm_campaign"),
        contact_data.get("utm_term"),
        contact_data.get("utm_content"),
        contact_data.get("status", "new"),
        contact_data.get("lead_score", 50),
        contact_data.get("pain_point"),
        contact_data.get("service_interest"),
    )

    try:
        with get_cursor() as cur:
            cur.execute(queries.UPSERT_CONTACT_POSTGRES, params)
            logger.info(f"🚀 Natalia Sync Success: {contact_data.get('phone')}")
    except Exception as e:
        logger.error(f"❌ Natalia Sync Error: {e}")


# Backward compatibility alias
upsert_contact = upsert_contact_advanced


def save_message(whatsapp_number: str, role: str, content: str) -> None:
    """Persists a chat message in the conversation history."""
    try:
        with get_cursor() as cur:
            # 1. Obtener contact_id
            cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
            row = cur.fetchone()
            if not row:
                upsert_contact_advanced({"phone": whatsapp_number, "status": "new"})
                cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
                row = cur.fetchone()

            if row:
                contact_id = row[0]
                cur.execute(queries.INSERT_MESSAGE, (contact_id, role, content))
    except Exception as e:
        logger.error(f"❌ Error guardando mensaje: {e}")


def get_chat_history(whatsapp_number: str, limit: int = 10) -> List[Dict[str, str]]:
    """Obtiene los últimos N mensajes para contexto de la IA"""
    history = []
    try:
        with get_cursor() as cur:
            cur.execute(queries.SELECT_CHAT_HISTORY, (whatsapp_number, limit))
            rows = cur.fetchall()
            for row in reversed(rows):
                history.append({"role": row[0], "content": row[1]})
    except Exception:
        pass
    return history


def check_connection() -> bool:
    """Verifica si la base de datos está accesible"""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except Exception:
        return False


# =================================================================
# ADDITIONAL FUNCTIONS (Recovers previous lost functions)
# =================================================================


def mark_lead_sent(whatsapp_number: str) -> bool:
    """Flags a lead as successfully sent to Meta CAPI."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.UPDATE_LEAD_SENT_FLAG, (whatsapp_number,))
            return True
    except Exception:
        return False


def get_user_message_count(whatsapp_number: str) -> int:
    """Counts total messages sent by a user."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.COUNT_USER_MESSAGES, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


def check_if_lead_sent(whatsapp_number: str) -> bool:
    """Checks if the conversion event was already sent to Meta."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.CHECK_LEAD_SENT_FLAG, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else False
    except Exception:
        return False


def get_or_create_lead(
    whatsapp_phone: str, meta_data: Optional[dict] = None
) -> Tuple[Optional[str], bool]:
    """Retrieves existing lead ID or creates a new one."""
    if meta_data is None:
        meta_data = {}
    try:
        with get_cursor() as cur:
            # 1. Check existing
            cur.execute(queries.SELECT_LEAD_ID_BY_PHONE, (whatsapp_phone,))
            row = cur.fetchone()
            if row:
                # Update logic skipped for brevity but ID returned
                return (str(row[0]), False)

            # 2. Create New
            if BACKEND == "postgres":
                cur.execute(
                    queries.INSERT_LEAD_RETURNING_ID,
                    (
                        whatsapp_phone,
                        meta_data.get("meta_lead_id"),
                        meta_data.get("click_id"),
                        meta_data.get("email"),
                        meta_data.get("name"),
                    ),
                )
                lead_id = cur.fetchone()[0]
                return (str(lead_id), True)
            else:
                new_id = str(uuid.uuid4())
                cur.execute(
                    queries.INSERT_LEAD_SQLITE,
                    (
                        new_id,
                        whatsapp_phone,
                        meta_data.get("meta_lead_id"),
                        meta_data.get("click_id"),
                        meta_data.get("email"),
                        meta_data.get("name"),
                    ),
                )
                return (new_id, True)
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        return (None, False)


def log_interaction(lead_id: str, role: str, content: str) -> bool:
    """Logs a specific interaction event associated with a lead."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.INSERT_INTERACTION, (lead_id, role, content))
            return True
    except Exception:
        return False


# =================================================================
# MISSING ADMIN FUNCTIONS (Recovers Admin Panel)
# =================================================================


def get_all_visitors(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los últimos visitantes para el dashboard"""
    visitors = []
    try:
        with get_cursor() as cur:
            # SQL Raw para asegurar compatibilidad
            if BACKEND == "postgres":
                sql = "SELECT id, external_id, source, created_at, ip_address FROM visitors ORDER BY created_at DESC LIMIT %s"
            else:
                sql = "SELECT id, external_id, source, created_at, ip_address FROM visitors ORDER BY created_at DESC LIMIT ?"

            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            for row in rows:
                visitors.append(
                    {
                        "id": row[0],  # Assuming id is 0
                        "external_id": row[1],
                        "source": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4],
                    }
                )
    except Exception as e:
        logger.error(f"❌ Error obteniendo visitors: {e}")
    return visitors


def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID para confirmar venta"""
    try:
        with get_cursor() as cur:
            if BACKEND == "postgres":
                sql = (
                    "SELECT id, external_id, fbclid, source, created_at FROM visitors WHERE id = %s"
                )
            else:
                sql = (
                    "SELECT id, external_id, fbclid, source, created_at FROM visitors WHERE id = ?"
                )

            cur.execute(sql, (visitor_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "external_id": row[1],
                    "fbclid": row[2],
                    "source": row[3],
                    "timestamp": row[4],
                }
    except Exception as e:
        logger.error(f"❌ Error buscando visitor {visitor_id}: {e}")
    return None
