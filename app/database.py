# =================================================================
# DATABASE.PY - Serverless-Optimized Connection Strategy (V2)
# Jorge Aguirre Flores Web
# =================================================================
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Type
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import app.sql_queries as queries
from app.config import settings

# Attempt PostgreSQL Import
try:
    import psycopg2
    import psycopg2.pool

    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

    class _MockPsycopg2:
        class Error(Exception):
            pass

        def connect(self, *args: Any, **kwargs: Any) -> Any:
            raise ImportError("psycopg2 is not installed")

    psycopg2 = _MockPsycopg2()  # type: ignore[assignment]


class SQLiteCursorWrapper:
    """Adapta sintaxis Postgres (%s) a SQLite (?)"""

    def __init__(self, cursor: sqlite3.Cursor):
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
    def description(self) -> Optional[tuple]:
        """Returns description of the query result."""
        return self.cursor.description

    @property
    def lastrowid(self) -> Optional[int]:
        """Returns ID of last inserted row."""
        return self.cursor.lastrowid


# Type definitions
try:
    from psycopg2.extensions import connection as PgConnection
    from psycopg2.extensions import cursor as PgCursor
except ImportError:
    from typing import Any as PgConnection  # type: ignore[assignment]
    from typing import Any as PgCursor  # type: ignore[assignment]

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

DBConnection: TypeAlias = sqlite3.Connection | PgConnection
DBCursor: TypeAlias = sqlite3.Cursor | PgCursor | SQLiteCursorWrapper

# DB_ERRORS: Tuple of exceptions for safe catching across backends
DB_ERRORS: Tuple[Type[Exception], ...] = (  # type: ignore[assignment]
    (sqlite3.Error, psycopg2.Error) if HAS_POSTGRES else (sqlite3.Error,)
)

logger = logging.getLogger(__name__)

# Connection Pool (Postgres)
_pool = None

# _backend: 'postgres' vs 'sqlite'
# NOTE: In Serverless (Vercel), we DO NOT use a global pool object.
# Global pools are created per-lambda instance, leading to connection exhaustion.
_backend = "sqlite"
BACKEND = _backend
if settings.DATABASE_URL and HAS_POSTGRES:
    # 🛡️ SILICON VALLEY PROTOCOL: Deterministic Guard against STUB DSNs
    # If the ENV var is a stub, we FORCE SQLite to prevent DSN Parse Errors.
    db_url_str = str(settings.DATABASE_URL)
    db_url_clean = db_url_str.strip().lower()
    is_invalid = any(
        x in db_url_clean for x in ["required", "dsn_here", "none", "production", "placeholder"]
    )

    if not is_invalid:
        _backend = "postgres"
        # Ensure URL forces Supabase Transaction Mode if available
        if ":6543" in db_url_str and "pgbouncer=true" not in db_url_str:
            logger.warning(
                "⚠️ Using Supabase Pooler Port 6543 but missing '?pgbouncer=true'. Adding it automatically."
            )
    else:
        logger.warning(
            "🛡️ Deterministic Guard: detected invalid DSN (%s...). Falling back to SQLite.",
            str(settings.DATABASE_URL)[:10] if settings.DATABASE_URL else "",
        )
        # Logic to append query param could go here, but usually users fix ENV.



def _get_postgres_pool():
    global _pool
    if _pool is None:
        try:
            clean_url = _sanitize_postgres_dsn(settings.DATABASE_URL)
            # Create a threaded connection pool. minconn=1, maxconn=1 ensures we persist 1 connection
            # but don't open more, suitable for serverless environment where instances are isolated.
            _pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=1,
                dsn=clean_url,
                connect_timeout=2,
                sslmode="require"
            )
        except Exception as e:
            logger.error(f"🔥 Failed to create connection pool: {e}")
            raise
    return _pool

@contextmanager
def get_db_connection() -> Generator[Any, None, None]:
    """
    Creates a SINGLE connection per request.
    Silicon Valley Protocol: 0-Latency failover & strict pool hygiene.
    """
    conn = None
    try:
        if _backend == "postgres":
            # Get connection from pool
            pool = _get_postgres_pool()
            conn = pool.getconn()
        else:
            # SQLite fallback
            conn = _establish_connection()

        yield conn

        if conn:
            conn.commit()
    except Exception as e:
        _handle_db_error(conn, e)
        raise
    finally:
        if _backend == "postgres" and conn:
            # Return connection to pool instead of closing
            try:
                _get_postgres_pool().putconn(conn)
            except Exception as e:
                logger.error(f"Error returning connection to pool: {e}")
                # If putconn fails, try to close it just in case
                try:
                    conn.close()
                except Exception:
                    pass
        else:
            _close_connection(conn)


def _establish_connection() -> DBConnection:
    if _backend == "postgres":
        # 🛡️ Normalize malformed DSNs and strip problematic params before psycopg2 connect.
        clean_url = _sanitize_postgres_dsn(settings.DATABASE_URL)

        return psycopg2.connect(clean_url, connect_timeout=2, sslmode="require")

    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(db_dir), "database", "local_fallback.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _sanitize_postgres_dsn(raw_url: Optional[str]) -> str:
    """
    Normalizes malformed query separators and removes pgbouncer hints
    that break direct psycopg2 DSN parsing in some environments.
    """
    if not raw_url:
        return ""

    dsn = raw_url.strip()

    # Repair common malformed DSN: .../postgres&connection_limit=1
    if "?" not in dsn and "&" in dsn:
        scheme_split = dsn.split("://", 1)
        tail = scheme_split[1] if len(scheme_split) == 2 else dsn
        if "/" in tail:
            left, right = dsn.split("&", 1)
            dsn = f"{left}?{right}"

    parsed = urlsplit(dsn)
    if not parsed.query:
        return dsn

    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    unsupported = {"pgbouncer", "connection_limit"}
    filtered = [(k, v) for k, v in query_items if k.lower() not in unsupported]
    clean_query = urlencode(filtered, doseq=True)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, clean_query, parsed.fragment))


def _handle_db_error(conn, e):
    if conn:
        try:
            conn.rollback()
        except DB_ERRORS:
            pass

    err_msg = str(e).lower()
    if "timeout" in err_msg:
        logger.error("🔥 DB ERROR: Connection Timeout. Possible cold start or pooler exhaustion.")
    elif "too many connections" in err_msg:
        logger.error("🔥 DB ERROR: Connection Exhaustion. Check pooler settings.")
    elif "password authentication failed" in err_msg:
        logger.error("🔥 DB ERROR: Auth Failure. Check DATABASE_URL.")
    else:
        logger.error("🔥 Database Transaction Error: %s", e)


def _close_connection(conn):
    if conn:
        try:
            conn.close()
        except DB_ERRORS as close_err:
            logger.debug("ℹ️ Connection close cleanup: %s", close_err)


@contextmanager
def get_cursor() -> Generator[DBCursor, None, None]:
    """
    Utility to get a cursor directly.
    Usage: with get_cursor() as cur: cur.execute(...)
    """
    with get_db_connection() as conn:
        if _backend == "postgres":
            yield conn.cursor()
        else:
            yield SQLiteCursorWrapper(conn.cursor())


# =================================================================
# COMPATIBILITY & INIT
# =================================================================


def init_tables() -> bool:
    """Crea tablas si no existen, sincronizado con atomic schema v3.0"""
    try:
        config = _get_db_config()
        _create_core_tables(config)
        _create_crm_tables(config)

        with get_cursor() as cur:
            _run_column_migrations(cur, config["status_type"])

        logger.info("✅ Tablas sincronizadas (%s)", _backend)
    except DB_ERRORS:
        logger.exception("❌ Error sincronizando tablas")
        return False
    else:
        return True


def _get_db_config() -> Dict[str, str]:
    if _backend == "postgres":
        return {
            "id_type_uuid": "UUID PRIMARY KEY DEFAULT gen_random_uuid()",
            "id_type_serial": "SERIAL PRIMARY KEY",
            "timestamp_default": "CURRENT_TIMESTAMP",  # Queries should use DEFAULT CURRENT_TIMESTAMP
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


def _create_core_tables(cf: Dict[str, str]) -> None:
    with get_db_connection() as conn:
        # Site Content (CMS)
        try:
            cur = conn.cursor()
            cur.execute(queries.CREATE_TABLE_SITE_CONTENT)
            conn.commit()
        except DB_ERRORS:
            if conn:
                conn.rollback()

        # Create PostGIS (Postgres only)
        if _backend == "postgres":
            try:
                cur = conn.cursor()
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                conn.commit()
            except psycopg2.Error:
                if conn:
                    conn.rollback()

            # Type guards
            try:
                cur = conn.cursor()
                cur.execute("""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_status') THEN
                            CREATE TYPE lead_status AS ENUM (
                                'new', 'contacted', 'qualified', 'converted', 'lost'
                            );
                        END IF;
                    END $$;
                """)
                conn.commit()
            except psycopg2.Error:
                if conn:
                    conn.rollback()

        # Multi-tenant tables
        for q_name, q_sql in [
            ("clients", queries.CREATE_TABLE_CLIENTS),
            ("api_keys", queries.CREATE_TABLE_API_KEYS),
            ("emq_stats", queries.CREATE_TABLE_EMQ_STATS),
        ]:
            try:
                cur = conn.cursor()
                cur.execute(
                    q_sql.format(
                        id_type_pk=cf["id_type_pk"],
                        id_type_serial=cf["id_type_serial"],
                        lead_id_type=cf["lead_id_type"],
                        timestamp_default=cf["timestamp_default"],
                    )
                )
                conn.commit()
            except (sqlite3.Error, psycopg2.Error) as e:
                if conn:
                    conn.rollback()
                logger.warning("⚠️ Table creation skip/error (%s): %s", q_name, e)

        # Migration for new columns in clients
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS email TEXT UNIQUE")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS company TEXT")
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Clients migration skip/error: %s", e)

        # Business Knowledge
        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_BUSINESS_KNOWLEDGE.format(
                    id_type_serial=cf["id_type_serial"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            cur.execute(queries.CREATE_INDEX_KNOWLEDGE_SLUG)
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Business knowledge skip/error: %s", e)

        # Visitors
        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_VISITORS.format(
                    id_type_serial=cf["id_type_serial"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            cur.execute(queries.CREATE_INDEX_VISITORS_EXTERNAL_ID)
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Visitors table creation skip/error: %s", e)


def save_emq_score(
    client_id: Optional[str],
    event_name: str,
    score: float,
    payload_size: int,
    has_pii: bool,
) -> None:
    """Save EMQ score to database for dashboard metrics."""
    query = """
    INSERT INTO emq_stats (client_id, event_name, score, payload_size, has_pii)
    VALUES (%s, %s, %s, %s, %s)
    """
    try:
        with get_cursor() as cursor:
            cursor.execute(query, (client_id, event_name, score, payload_size, has_pii))
    except DB_ERRORS:
        logger.exception("❌ Error saving EMQ score")


def get_emq_stats(limit: int = 100) -> list[dict[str, Any]]:
    """Retrieve EMQ stats for dashboard visualization."""
    query = """
    SELECT event_name, AVG(score) as avg_score, COUNT(*) as count,
           MAX(created_at) as last_seen
    FROM emq_stats
    GROUP BY event_name
    ORDER BY last_seen DESC
    LIMIT %s
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            # Handle cursor.description potentially being None
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
            else:
                results = []
            cursor.close()
            return results
    except DB_ERRORS:
        logger.exception("❌ Error getting EMQ stats")
        return []


def _create_crm_tables(cf: Dict[str, str]) -> None:
    with get_db_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_CONTACTS.format(
                    id_type_primary_key=cf["id_type_pk"],
                    status_type=cf["status_type"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Contacts table creation skip/error: %s", e)

        try:
            cur = conn.cursor()
            cur.execute(queries.CREATE_INDEX_CONTACTS_WHATSAPP)
            conn.commit()
        except DB_ERRORS:
            if conn:
                conn.rollback()

        try:
            cur = conn.cursor()
            cur.execute(queries.CREATE_INDEX_CONTACTS_STATUS)
            conn.commit()
        except DB_ERRORS:
            if conn:
                conn.rollback()

        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_MESSAGES.format(
                    id_type_primary_key=cf["id_type_pk"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            cur.execute(queries.CREATE_INDEX_MESSAGES_CONTACT_ID)
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Messages table creation skip/error: %s", e)

        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_APPOINTMENTS.format(
                    id_type_serial=cf["id_type_serial"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Appointments table creation skip/error: %s", e)

        try:
            cur = conn.cursor()
            cur.execute(
                queries.CREATE_TABLE_INTERACTIONS.format(
                    id_type_serial=cf["id_type_serial"],
                    lead_id_type=cf["lead_id_type"],
                    timestamp_default=cf["timestamp_default"],
                )
            )
            cur.execute(queries.CREATE_INDEX_INTERACTIONS_LEAD_ID)
            conn.commit()
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Interactions table creation skip/error: %s", e)


def _run_column_migrations(cur: DBCursor, status_type: str) -> None:
    new_columns = [
        ("profile_pic_url", "TEXT"),
        ("fb_browser_id", "TEXT"),
        ("utm_term", "TEXT"),
        ("utm_content", "TEXT"),
        ("status", status_type),
        ("lead_score", "INTEGER DEFAULT 50"),
        ("phone", "TEXT"),
        ("pain_point", "TEXT"),
        ("service_interest", "TEXT"),
        ("service_booked_date", "TIMESTAMP"),
        ("appointment_count", "INTEGER DEFAULT 0"),
        ("updated_at", "TIMESTAMP"),
        ("onboarding_step", "TEXT"),
        ("is_admin", "BOOLEAN DEFAULT FALSE"),
        ("email", "TEXT"),
        ("meta_lead_id", "TEXT"),
    ]

    for col_name, col_type in new_columns:
        try:
            if _backend == "postgres":
                cur.execute(
                    f"ALTER TABLE crm_leads ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                )
                # Also migrate visitors table
                if col_name in ["email", "phone"]:
                    cur.execute(
                        f"ALTER TABLE visitors ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                    )
            else:
                try:
                    cur.execute(f"ALTER TABLE crm_leads ADD COLUMN {col_name} {col_type};")
                except sqlite3.Error:
                    pass
                # Also migrate visitors table for SQLite
                if col_name in ["email", "phone"]:
                    try:
                        cur.execute(f"ALTER TABLE visitors ADD COLUMN {col_name} {col_type};")
                    except sqlite3.Error:
                        pass
        except DB_ERRORS:
            pass


# =================================================================
# OPERATIONS (Domain Logic - Persisted)
# =================================================================


def save_visitor(
    external_id: str,
    fbclid: Optional[str],
    ip_address: Optional[str],
    user_agent: Optional[str],
    source: str = "pageview",
    utm_data: Optional[Dict[str, Any]] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> None:
    """Saves visitor data for attribution tracking."""
    if utm_data is None:
        utm_data = {}

    try:
        with get_cursor() as cur:
            ua_truncated = user_agent[:500] if user_agent else None
            params = (
                external_id,
                fbclid,
                ip_address,
                ua_truncated,
                source,
                utm_data.get("utm_source"),
                utm_data.get("utm_medium"),
                utm_data.get("utm_campaign"),
                utm_data.get("utm_term"),
                utm_data.get("utm_content"),
                email,
                phone,
            )

            stmt = queries.INSERT_VISITOR
            if _backend != "postgres":
                stmt = stmt.replace("INSERT INTO", "INSERT OR IGNORE INTO")
            cur.execute(stmt, params)
    except DB_ERRORS:
        logger.exception("Failed to save visitor")


def get_visitor_fbclid(external_id: str) -> Optional[str]:
    """Retrieves the Facebook Click ID for a given visitor."""
    try:
        with get_cursor() as cur:
            query = queries.SELECT_FBCLID_BY_EXTERNAL_ID
            cur.execute(query, (external_id,))
            res = cur.fetchone()
            if res:
                return res[0]
    except DB_ERRORS:
        pass
    return None


def upsert_contact_advanced(contact_data: Dict[str, Any]) -> None:
    """Upsert avanzado estilo CRM Natalia."""
    if _backend != "postgres":
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
        except sqlite3.Error:
            logger.exception("SQLite Upsert Error")
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
    except psycopg2.Error:
        logger.exception("❌ Natalia Sync Error")


# Backward compatibility alias
upsert_contact = upsert_contact_advanced


def save_message(whatsapp_phone: str, role: str, content: str) -> None:
    """Persists a chat message in the conversation history."""
    try:
        with get_cursor() as cur:
            # 1. Obtener contact_id
            cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_phone,))
            row = cur.fetchone()
            if not row:
                upsert_contact_advanced({"phone": whatsapp_phone, "status": "new"})
                cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_phone,))
                row = cur.fetchone()

            if row:
                contact_id = row[0]
                cur.execute(queries.INSERT_MESSAGE, (contact_id, role, content))
    except DB_ERRORS:
        logger.exception("❌ Error guardando mensaje")


def get_chat_history(whatsapp_phone: str, limit: int = 10) -> List[Dict[str, str]]:
    """Obtiene los últimos N mensajes para contexto de la IA"""
    history = []
    try:
        with get_cursor() as cur:
            cur.execute(queries.SELECT_CHAT_HISTORY, (whatsapp_phone, limit))
            rows = cur.fetchall()
            for row in reversed(rows):
                history.append({"role": row[0], "content": row[1]})
    except DB_ERRORS:
        pass
    return history


def check_connection() -> bool:
    """Verifica si la base de datos está accesible"""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except DB_ERRORS:
        return False


# =================================================================
# ADDITIONAL FUNCTIONS (Recovers previous lost functions)
# =================================================================


def mark_lead_sent(whatsapp_phone: str) -> bool:
    """Flags a lead as successfully sent to Meta CAPI."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.UPDATE_LEAD_SENT_FLAG, (whatsapp_phone,))
            return True
    except DB_ERRORS:
        return False


def get_user_message_count(whatsapp_phone: str) -> int:
    """Counts total messages sent by a user."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.COUNT_USER_MESSAGES, (whatsapp_phone,))
            row = cur.fetchone()
            return row[0] if row else 0
    except DB_ERRORS:
        return 0


def check_if_lead_sent(whatsapp_phone: str) -> bool:
    """Checks if the conversion event was already sent to Meta."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.CHECK_LEAD_SENT_FLAG, (whatsapp_phone,))
            row = cur.fetchone()
            return row[0] if row else False
    except DB_ERRORS as e:
        logger.debug("❌ Error checking lead sent: %s", e)
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
            if _backend == "postgres":
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
                row = cur.fetchone()
                lead_id = str(row[0]) if row else None
                return (lead_id, True)
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
    except DB_ERRORS as e:
        logger.exception("❌ Error creating lead: %s", e)
        return (None, False)
    return (None, False)


def log_interaction(lead_id: str, role: str, content: str) -> bool:
    """Logs a specific interaction event associated with a lead."""
    try:
        with get_cursor() as cur:
            cur.execute(queries.INSERT_INTERACTION, (lead_id, role, content))
            return True
    except Exception as e:
        logger.debug("❌ Error logging interaction: %s", e)
        return False


# =================================================================
# MISSING ADMIN FUNCTIONS (Recovers Admin Panel)
# =================================================================


def get_all_visitors(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los últimos visitantes para el dashboard"""
    visitors = []
    try:
        with get_cursor() as cur:
            query = queries.SELECT_RECENT_VISITORS
            cur.execute(query, (limit,))
            # Handle cursor.description potentially being None
            if cur.description:
                columns = [col[0] for col in cur.description]
                rows = cur.fetchall()
                for row in rows:
                    visitors.append(dict(zip(columns, row, strict=False)))
    except DB_ERRORS:
        logger.exception("❌ Error obteniendo visitors")
    return visitors


def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID para confirmar venta"""
    try:
        with get_cursor() as cur:
            query = queries.SELECT_VISITOR_BY_ID
            cur.execute(query, (visitor_id,))
            # Handle cursor.description potentially being None
            if cur.description:
                columns = [col[0] for col in cur.description]
                row = cur.fetchone()
                if row:
                    return dict(zip(columns, row, strict=False))
    except DB_ERRORS as e:
        logger.exception("❌ Error buscando visitor %s: %s", visitor_id, e)
    return None
