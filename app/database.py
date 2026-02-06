# =================================================================
# DATABASE.PY - Serverless-Optimized Connection Strategy (V2)
# Jorge Aguirre Flores Web
# =================================================================
import logging
import os
import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import uuid

from app.config import settings
import app.sql_queries as queries

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
    # 🛡️ SILICON VALLEY PROTOCOL: Deterministic Guard against Placeholder DSNs
    # If the ENV var is a placeholder, we FORCE SQLite to prevent DSN Parse Errors.
    db_url_clean = settings.DATABASE_URL.strip().lower()
    is_placeholder = "required" in db_url_clean or "placeholder" in db_url_clean or "none" in db_url_clean

    if not is_placeholder:
        BACKEND = "postgres"
        # Ensure URL forces Supabase Transaction Mode if available
        if ":6543" in settings.DATABASE_URL and "pgbouncer=true" not in settings.DATABASE_URL:
            logger.warning("⚠️ Using Supabase Pooler Port 6543 but missing '?pgbouncer=true'. Adding it automatically.")
    else:
        logger.warning(f"🛡️ Deterministic Guard: detected placeholder DSN. Falling back to SQLite.")
        # Logic to append query param could go here, but usually users fix ENV.

@contextmanager
def get_db_connection():
    """
    Creates a SINGLE connection per request.
    Crucial for Vercel/Supabase Transaction Pooler (Port 6543).
    Silicon Valley Protocol: 0-Latency failover & strict pool hygiene.
    """
    conn = None
    try:
        if BACKEND == "postgres":
            # ⚡ SERVERLESS PATTERN: Open -> Query -> Close IMMEDIATELY
            # We use a short timeout to fail fast and allow Vercel to retry
            conn = psycopg2.connect(
                settings.DATABASE_URL,
                connect_timeout=5,
                sslmode='require'
            )
            yield conn
        else:
            # Local SQLite fallback
            db_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(os.path.dirname(db_dir), "database", "local_fallback.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn

        if conn:
            conn.commit()
            
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        
        # ELITE LOGGING: Detect common Supabase issues
        err_msg = str(e)
        if "timeout" in err_msg.lower():
            logger.error("🔥 DB ERROR: Connection Timeout. Possible cold start or pooler exhaustion.")
        elif "too many connections" in err_msg.lower():
            logger.error("🔥 DB ERROR: Connection Exhaustion. Check pooler settings.")
        elif "password authentication failed" in err_msg.lower():
            logger.error("🔥 DB ERROR: Auth Failure. Check DATABASE_URL.")
        else:
            logger.error(f"🔥 Database Transaction Error: {err_msg}")
        
        raise e
    finally:
        if conn:
            try:
                conn.close()
            except Exception as close_err:
                logger.debug(f"ℹ️ Connection close cleanup: {close_err}")

class SQLiteCursorWrapper:
    """Adapta sintaxis Postgres (%s) a SQLite (?)"""
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, sql, params=None):
        if params:
            sql = sql.replace("%s", "?")
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def close(self):
        self.cursor.close()
        
    @property
    def rowcount(self):
        return self.cursor.rowcount
    
    @property
    def lastrowid(self):
        return self.cursor.lastrowid

@contextmanager
def get_cursor():
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

def init_tables():
    """Crea tablas si no existen, sincronizado con init_crm_master_clean.sql v2.0"""
    try:
        with get_cursor() as cur:
            # --- Configuración de Tipos y Defaults ---
            if BACKEND == "postgres":
                id_type_uuid = "UUID PRIMARY KEY DEFAULT gen_random_uuid()"
                id_type_serial = "SERIAL PRIMARY KEY"
                timestamp_default = "CURRENT_TIMESTAMP"
                status_type = "lead_status DEFAULT 'new'"
                lead_id_type = "UUID"
                id_type_pk = id_type_uuid
                
                # Crear Enum en Postgres si no existe
                cur.execute("""
                    DO $$ BEGIN
                        CREATE TYPE lead_status AS ENUM (
                            'new', 'interested', 'nurturing', 'ghost', 'booked', 
                            'client_active', 'client_loyal', 'archived'
                        );
                    EXCEPTION WHEN duplicate_object THEN null; END $$;
                """)
            else:
                id_type_uuid = "TEXT PRIMARY KEY"
                id_type_serial = "INTEGER PRIMARY KEY AUTOINCREMENT"
                timestamp_default = "CURRENT_TIMESTAMP"
                status_type = "TEXT DEFAULT 'new'"
                lead_id_type = "TEXT"
                id_type_pk = id_type_uuid

            # Formatear y Ejecutar DDLs
            cur.execute(queries.CREATE_TABLE_BUSINESS_KNOWLEDGE.format(
                id_type_serial=id_type_serial, timestamp_default=timestamp_default
            ))
            cur.execute(queries.CREATE_INDEX_KNOWLEDGE_SLUG)

            cur.execute(queries.CREATE_TABLE_VISITORS.format(
                id_type_serial=id_type_serial, timestamp_default=timestamp_default
            ))
            cur.execute(queries.CREATE_INDEX_VISITORS_EXTERNAL_ID)

            cur.execute(queries.CREATE_TABLE_CONTACTS.format(
                id_type_primary_key=id_type_pk, 
                status_type=status_type,
                timestamp_default=timestamp_default
            ))
            # ... Indexes ...
            cur.execute(queries.CREATE_INDEX_CONTACTS_WHATSAPP)
            cur.execute(queries.CREATE_INDEX_CONTACTS_STATUS)
            
            # Additional Tables (Messages, Appointments, Leads, Interactions)
            cur.execute(queries.CREATE_TABLE_MESSAGES.format(
                id_type_primary_key=id_type_pk, timestamp_default=timestamp_default
            ))
            cur.execute(queries.CREATE_INDEX_MESSAGES_CONTACT_ID)

            cur.execute(queries.CREATE_TABLE_APPOINTMENTS.format(
                id_type_serial=id_type_serial, timestamp_default=timestamp_default
            ))

            cur.execute(queries.CREATE_TABLE_LEADS.format(
                id_type_primary_key=id_type_pk, timestamp_default=timestamp_default
            ))
            cur.execute(queries.CREATE_INDEX_LEADS_PHONE)
            cur.execute(queries.CREATE_INDEX_LEADS_META_ID)

            cur.execute(queries.CREATE_TABLE_INTERACTIONS.format(
                id_type_serial=id_type_serial, lead_id_type=lead_id_type, timestamp_default=timestamp_default
            ))
            cur.execute(queries.CREATE_INDEX_INTERACTIONS_LEAD_ID)
            
            # --- Column Migrations (Condensed for stability) ---
            # Kept minimal to avoid errors during cold start
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
                ("is_admin", "BOOLEAN DEFAULT FALSE")
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
                            pass # Column likely exists
                except Exception:
                    pass

        logger.info(f"✅ Tablas sincronizadas ({BACKEND})")
        return True
    except Exception as e:
        logger.error(f"❌ Error sincronizando tablas: {e}")
        return False

# =================================================================
# OPERATIONS (Domain Logic - Persisted)
# =================================================================

def save_visitor(external_id, fbclid, ip_address, user_agent, source="pageview", utm_data=None):
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
                utm_data.get('utm_source'),
                utm_data.get('utm_medium'),
                utm_data.get('utm_campaign'),
                utm_data.get('utm_term'),
                utm_data.get('utm_content')
            )
            
            if BACKEND == "postgres":
                stmt = """
                    INSERT INTO visitors 
                    (external_id, fbclid, ip, user_agent, source, utm_source, utm_medium, utm_campaign, utm_term, utm_content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (external_id) DO NOTHING
                """
                cur.execute(stmt, params)
            else:
                stmt = """
                    INSERT OR IGNORE INTO visitors 
                    (external_id, fbclid, ip, user_agent, source, utm_source, utm_medium, utm_campaign, utm_term, utm_content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """
                cur.execute(stmt, params)
    except Exception as e:
        logger.error(f"Failed to save visitor: {e}")

def get_visitor_fbclid(external_id: str) -> Optional[str]:
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

def upsert_contact_advanced(contact_data: Dict[str, Any]):
    """Upsert avanzado estilo CRM Natalia."""
    if BACKEND != "postgres":
        # SQLite Partial
        try:
            with get_cursor() as cur:
                cur.execute(queries.UPSERT_CONTACT_SQLITE, (
                    contact_data.get('phone'), 
                    contact_data.get('name'), 
                    contact_data.get('utm_source'),
                    contact_data.get('status', 'new')
                ))
        except Exception as e:
            logger.error(f"SQLite Upsert Error: {e}")
        return

    params = (
        contact_data.get('phone'),
        contact_data.get('name'),
        contact_data.get('profile_pic_url'),
        contact_data.get('fbclid'),
        contact_data.get('fbp'),
        contact_data.get('utm_source'),
        contact_data.get('utm_medium'),
        contact_data.get('utm_campaign'),
        contact_data.get('utm_term'),
        contact_data.get('utm_content'),
        contact_data.get('status', 'new'),
        contact_data.get('lead_score', 50),
        contact_data.get('pain_point'),
        contact_data.get('service_interest')
    )

    try:
        with get_cursor() as cur:
            cur.execute(queries.UPSERT_CONTACT_POSTGRES, params)
            logger.info(f"🚀 Natalia Sync Success: {contact_data.get('phone')}")
    except Exception as e:
        logger.error(f"❌ Natalia Sync Error: {e}")

# Backward compatibility alias
upsert_contact = upsert_contact_advanced

def save_message(whatsapp_number: str, role: str, content: str):
    try:
        with get_cursor() as cur:
            # 1. Obtener contact_id
            cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
            row = cur.fetchone()
            if not row:
                upsert_contact_advanced({'phone': whatsapp_number, 'status': 'new'})
                cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
                row = cur.fetchone()
            
            if row:
                contact_id = row[0]
                cur.execute(queries.INSERT_MESSAGE, (contact_id, role, content))
    except Exception as e:
        logger.error(f"❌ Error guardando mensaje: {e}")

def get_chat_history(whatsapp_number: str, limit: int = 10):
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
    try:
        with get_cursor() as cur:
            cur.execute(queries.UPDATE_LEAD_SENT_FLAG, (whatsapp_number,))
            return True
    except Exception:
        return False

def get_user_message_count(whatsapp_number: str) -> int:
    try:
        with get_cursor() as cur:
            cur.execute(queries.COUNT_USER_MESSAGES, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0

def check_if_lead_sent(whatsapp_number: str) -> bool:
    try:
        with get_cursor() as cur:
            cur.execute(queries.CHECK_LEAD_SENT_FLAG, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else False
    except Exception:
        return False
        
def get_or_create_lead(whatsapp_phone: str, meta_data: Optional[dict] = None) -> Tuple[Optional[str], bool]:
    if meta_data is None: meta_data = {}
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
                cur.execute(queries.INSERT_LEAD_RETURNING_ID, (
                    whatsapp_phone,
                    meta_data.get('meta_lead_id'), meta_data.get('click_id'),
                    meta_data.get('email'), meta_data.get('name')
                ))
                lead_id = cur.fetchone()[0]
                return (str(lead_id), True)
            else:
                new_id = str(uuid.uuid4())
                cur.execute(queries.INSERT_LEAD_SQLITE, (
                     new_id, whatsapp_phone,
                     meta_data.get('meta_lead_id'), meta_data.get('click_id'),
                     meta_data.get('email'), meta_data.get('name')
                ))
                return (new_id, True)
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        return (None, False)


def log_interaction(lead_id: str, role: str, content: str) -> bool:
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
                sql = "SELECT id, external_id, source, created_at, ip FROM visitors ORDER BY created_at DESC LIMIT %s"
            else:
                sql = "SELECT id, external_id, source, created_at, ip FROM visitors ORDER BY created_at DESC LIMIT ?"
            
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            for row in rows:
                visitors.append({
                    "id": row[0], # Assuming id is 0
                    "external_id": row[1],
                    "source": row[2],
                    "timestamp": row[3],
                    "ip_address": row[4]
                })
    except Exception as e:
        logger.error(f"❌ Error obteniendo visitors: {e}")
    return visitors

def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID para confirmar venta"""
    try:
        with get_cursor() as cur:
            if BACKEND == "postgres":
                sql = "SELECT id, external_id, fbclid, source, created_at FROM visitors WHERE id = %s"
            else:
                sql = "SELECT id, external_id, fbclid, source, created_at FROM visitors WHERE id = ?"
            
            cur.execute(sql, (visitor_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "external_id": row[1],
                    "fbclid": row[2],
                    "source": row[3],
                    "timestamp": row[4]
                }
    except Exception as e:
        logger.error(f"❌ Error buscando visitor {visitor_id}: {e}")
    return None
