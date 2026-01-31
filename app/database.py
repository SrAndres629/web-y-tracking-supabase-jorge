# =================================================================
# DATABASE.PY - Gestión Híbrida PostgreSQL / SQLite
# Jorge Aguirre Flores Web
# =================================================================
import logging
import os
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import uuid

from app.config import settings
import app.sql_queries as queries  # Importamos el repo de queries

# Intentar importar psycopg2 (PostgreSQL)
try:
    import psycopg2
    from psycopg2 import pool
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

logger = logging.getLogger(__name__)

# Pool Global
_pg_pool: Optional[Any] = None

# Tipo de Backend Activo
BACKEND = "sqlite"  # 'postgres' o 'sqlite'

def init_pool() -> bool:
    """Inicializa la conexión a BD (Nube o Local)"""
    global _pg_pool, BACKEND
    
    is_prod = os.getenv("VERCEL") or os.getenv("RENDER") or os.getenv("ENVIRONMENT") == "production"
    
    # 1. Intentar PostgreSQL (Capacidad Crítica)
    if settings.DATABASE_URL and HAS_POSTGRES:
        try:
            _pg_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.DATABASE_URL,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            BACKEND = "postgres"
            logger.info("✅ PRODUCTION DATABASE: PostgreSQL connection established.")
            return True
        except Exception as e:
            logger.critical(f"🔥 FATAL: PostgreSQL connection failed: {e}")
            if is_prod:
                raise RuntimeError("PRODUCTION LOCKDOWN: Database connection required. Halting process to prevent data loss.")
    
    # 2. Fallback Controlado (Solo Desarrollo Local)
    if is_prod:
        logger.critical("🔥 FATAL: DATABASE_URL missing in production runtime.")
        raise RuntimeError("PRODUCTION LOCKDOWN: DATABASE_URL must be configured in Vercel/Render dashboard.")

    BACKEND = "sqlite"
    logger.warning("🧪 LOCAL DEV: Using SQLite (Data will be ephemeral if deployed).")
    return True

@contextmanager
def get_cursor():
    """
    Obtiene un cursor con:
    1. Auto-Reconnect: Si la conexión está muerta, pide otra.
    2. Health Check: Ejecuta 'SELECT 1' antes de entregarla.
    3. Retry Logic: Reintenta hasta 3 veces si falla.
    """
    conn = None
    max_retries = 3
    is_postgres = (BACKEND == "postgres")
    
    last_error = None

    # RETRY LOOP
    for attempt in range(max_retries):
        try:
            if is_postgres:
                if _pg_pool is None:
                    if not init_pool():
                        raise Exception("Postgres Pool not initialized")

                # 1. Get Connection
                conn = _pg_pool.getconn()
                
                # 2. Health Check (Ping)
                is_healthy = False
                if conn.closed == 0:
                    try:
                        with conn.cursor() as test_cur:
                            test_cur.execute("SELECT 1")
                        is_healthy = True
                    except Exception:
                        pass # Ping failed
                
                if not is_healthy:
                    # Connection dead, discard and retry
                    logger.warning(f"⚠️ DB Connection dead (Attempt {attempt+1}/{max_retries}). Discarding...")
                    try:
                        _pg_pool.putconn(conn, close=True)
                    except: pass
                    conn = None
                    continue # Try next attempt (will get new conn from pool)

                # 3. Yield to Caller
                yield conn.cursor()
                conn.commit()
                return # Success!
                
            else:
                # SQLite Mode (Local Dev Only)
                import os
                if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                    raise RuntimeError("PRODUCTION LOCKDOWN: SQLite fallback blocked in Vercel. Connect Supabase.")
                
                db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
                os.makedirs(db_dir, exist_ok=True)
                db_path = os.path.join(db_dir, "local_fallback.db")
                conn = sqlite3.connect(db_path)
                yield SQLiteCursorWrapper(conn.cursor())
                conn.commit()
                return # Success

        except Exception as e:
            last_error = e
            logger.error(f"❌ Error DB (Attempt {attempt+1}/{max_retries}): {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception: pass
                
                # Return/Close bad connection
                if is_postgres and _pg_pool:
                    try:
                        _pg_pool.putconn(conn, close=True) 
                    except: pass
                elif not is_postgres:
                    try:
                        conn.close()
                    except: pass
                conn = None
            
            # Don't sleep on last attempt
            if attempt < max_retries - 1:
                import time
                time.sleep(0.5)
    
    # If we got here, all retries failed
    logger.critical("🔥 CRITICAL: Database unreachable after retries.")
    raise last_error

class SQLiteCursorWrapper:
    """Adapta sintaxis Postgres (%s) a SQLite (?)"""
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, sql, params=None):
        # Traducción simple de query params
        if params:
            # Reemplazar %s por ?
            sql = sql.replace("%s", "?")
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def close(self):
        self.cursor.close()

def init_tables():
    """Crea tablas si no existen, sincronizado con init_crm_master_clean.sql v2.0"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
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

            # --- Migración de Columnas (Si ya existe la tabla) ---
            # Este bloque se mantiene igual por ser lógica condicional compleja, no SQL puro
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
                        cur.execute(f"PRAGMA table_info(contacts);")
                        cols = [c[1] for c in cur.fetchall()]
                        if col_name not in cols:
                            cur.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type};")
                except Exception as e:
                    logger.warning(f"⚠️ Nota: Al intentar añadir {col_name}: {e}")

            cur.execute(queries.CREATE_INDEX_CONTACTS_WHATSAPP)
            cur.execute(queries.CREATE_INDEX_CONTACTS_STATUS)

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
            
        logger.info(f"✅ Tablas sincronizadas con Schema Natalia v2.0 ({BACKEND})")
        return True
    except Exception as e:
        logger.error(f"❌ Error sincronizando tablas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# =================================================================
# OPERATIONS
# =================================================================

def save_visitor(external_id, fbclid, ip_address, user_agent, source="pageview", utm_data=None):
    if utm_data is None:
        utm_data = {}
        
    with get_cursor() as cur:
        if cur:
            cur.execute(
                queries.INSERT_VISITOR,
                (
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
            )

def upsert_contact_advanced(contact_data: Dict[str, Any]):
    """
    Upsert avanzado estilo CRM Natalia. Sincroniza marketing y ventas.
    """
    if BACKEND != "postgres":
        # Implementación parcial para SQLite
        with get_cursor() as cur:
            if cur:
                cur.execute(queries.UPSERT_CONTACT_SQLITE, (
                    contact_data.get('phone'), 
                    contact_data.get('name'), 
                    contact_data.get('utm_source'),
                    contact_data.get('status', 'new')
                ))
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
            if cur:
                cur.execute(queries.UPSERT_CONTACT_POSTGRES, params)
                logger.info(f"🚀 Natalia Sync Success: {contact_data.get('phone')}")
    except Exception as e:
        logger.error(f"❌ Natalia Sync Error: {e}")

# Backward compatibility alias
upsert_contact = upsert_contact_advanced

def save_message(whatsapp_number: str, role: str, content: str):
    """Guarda un mensaje en el historial para memoria de Natalia"""
    try:
        with get_cursor() as cur:
            if not cur: return
            
            # 1. Obtener contact_id
            cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
            row = cur.fetchone()
            if not row:
                # Si no existe, lo creamos mínimo
                upsert_contact_advanced({'phone': whatsapp_number, 'status': 'new'})
                cur.execute(queries.SELECT_CONTACT_ID_BY_PHONE, (whatsapp_number,))
                row = cur.fetchone()
            
            contact_id = row[0]
            
            # 2. Insertar mensaje
            cur.execute(queries.INSERT_MESSAGE, (contact_id, role, content))
    except Exception as e:
        logger.error(f"❌ Error guardando mensaje: {e}")

def get_chat_history(whatsapp_number: str, limit: int = 10):
    """Obtiene los últimos N mensajes para contexto de la IA"""
    history = []
    try:
        with get_cursor() as cur:
            if not cur: return []
            cur.execute(queries.SELECT_CHAT_HISTORY, (whatsapp_number, limit))
            rows = cur.fetchall()
            # Invertir para que sea cronológico
            for row in reversed(rows):
                history.append({"role": row[0], "content": row[1]})
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {e}")
    return history


def get_visitor_fbclid(external_id):
    with get_cursor() as cur:
        if cur:
            cur.execute(queries.SELECT_FBCLID_BY_EXTERNAL_ID, (external_id,))
            row = cur.fetchone()
            return row[0] if row else None
    return None

def initialize():
    if init_pool():
        init_tables()
        return True
    return False

def get_all_visitors(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los últimos visitantes para el dashboard"""
    visitors = []
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute(queries.SELECT_RECENT_VISITORS, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    visitors.append({
                        "id": row[0],
                        "external_id": row[1],
                        "source": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4]
                    })
    except Exception as e:
        logger.error(f"❌ Error obteniendo visitors: {e}")
    return visitors

def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID"""
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute(queries.SELECT_VISITOR_BY_ID, (visitor_id,))
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

# =================================================================
# W-003 TRACKING OPERATIONS (Tracking Rescue)
# =================================================================

def mark_lead_sent(whatsapp_number: str) -> bool:
    """Marca a un usuario como ya enviado a Meta para evitar duplicados (Senior Guard)"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            cur.execute(queries.UPDATE_LEAD_SENT_FLAG, (whatsapp_number,))
            return True
    except Exception as e:
        logger.error(f"❌ Error marcando lead enviado: {e}")
        return False

def get_user_message_count(whatsapp_number: str) -> int:
    """Cuenta cuántos mensajes ha enviado el USUARIO para el filtro de calidad"""
    try:
        with get_cursor() as cur:
            if not cur: return 0
            cur.execute(queries.COUNT_USER_MESSAGES, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        logger.error(f"❌ Error contando mensajes: {e}")
        return 0

def check_if_lead_sent(whatsapp_number: str) -> bool:
    """Verifica si ya pagamos a Meta por este Lead (Financial Shield)"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            cur.execute(queries.CHECK_LEAD_SENT_FLAG, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else False
    except Exception as e:
        logger.error(f"❌ Error verificando lead enviado: {e}")
        return False

def get_meta_data_by_ref(ref_tag: str) -> Optional[Dict[str, Any]]:
    """Recupera cookies fbc/fbp usando el [Ref Tag] del mensaje de WA"""
    try:
        with get_cursor() as cur:
            if not cur: return None
            cur.execute(queries.SELECT_META_DATA_BY_REF, (f"{ref_tag}%",))
            row = cur.fetchone()
            if row:
                return {
                    "fbclid": row[0],
                    "user_agent": row[1],
                    "ip_address": row[2],
                    "utm_source": row[3],
                    "utm_medium": row[4],
                    "utm_campaign": row[5]
                }
    except Exception as e:
        logger.error(f"❌ Error buscando meta data por ref: {e}")
    return None

def get_or_create_lead(whatsapp_phone: str, meta_data: Optional[dict] = None) -> tuple[Optional[str], bool]:
    """
    Obtiene o crea un Lead basado en el teléfono.
    Vincula datos de Meta (Click ID, Lead ID) si se proveen.
    Retorna tupla: (lead_id, is_new) donde is_new=True si fue recién creado.
    """
    if meta_data is None:
        meta_data = {}

    try:
        with get_cursor() as cur:
            if not cur: return (None, False)

            # 1. Buscar Lead existente
            cur.execute(queries.SELECT_LEAD_ID_BY_PHONE, (whatsapp_phone,))
            row = cur.fetchone()

            if row:
                lead_id = row[0]
                # Update si hay nuevos datos de Meta
                if meta_data:
                    cur.execute(queries.UPDATE_LEAD_METADATA, (
                        meta_data.get('meta_lead_id'),
                        meta_data.get('click_id'),
                        meta_data.get('email'),
                        meta_data.get('name'),
                        lead_id
                    ))
                return (str(lead_id), False)  # Existing lead

            # 2. Crear Nuevo Lead
            logger.info(f"✨ Creando Nuevo Lead: {whatsapp_phone}")
            if BACKEND == "postgres":
                cur.execute(queries.INSERT_LEAD_RETURNING_ID, (
                    whatsapp_phone,
                    meta_data.get('meta_lead_id'),
                    meta_data.get('click_id'),
                    meta_data.get('email'),
                    meta_data.get('name')
                ))
                lead_id = cur.fetchone()[0]
                return (str(lead_id), True)  # New lead created
            else:
                # SQLite Logic
                new_id = str(uuid.uuid4())
                cur.execute(queries.INSERT_LEAD_SQLITE, (
                    new_id,
                    whatsapp_phone,
                    meta_data.get('meta_lead_id'),
                    meta_data.get('click_id'),
                    meta_data.get('email'),
                    meta_data.get('name')
                ))
                return (new_id, True)  # New lead created

    except Exception as e:
        logger.error(f"❌ Error en get_or_create_lead: {e}")
        return (None, False)

def log_interaction(lead_id: str, role: str, content: str) -> bool:
    """Registra una interacción (mensaje) para el Lead"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            cur.execute(queries.INSERT_INTERACTION, (lead_id, role, content))
            return True
    except Exception as e:
        logger.error(f"❌ Error en log_interaction: {e}")
        return False



def check_connection() -> bool:
    """Verifica si la base de datos está accesible"""
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute("SELECT 1")
                return True
    except Exception as e:
        logger.error(f"❌ Health Check Failed: {e}")
    return False

# =================================================================
# NATALIA KNOWLEDGE BASE
# =================================================================

def save_knowledge_fact(slug: str, category: str, content: str):
    """Guarda o actualiza un hecho en la base de conocimiento"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
            if BACKEND == "postgres":
                sql = queries.UPSERT_KNOWLEDGE_POSTGRES
            else:
                sql = queries.UPSERT_KNOWLEDGE_SQLITE
                
            cur.execute(sql, (slug, category, content))
            logger.info(f"🧠 Natalia Learned: {slug} ({category})")
            return True
    except Exception as e:
        logger.error(f"❌ Error guardando conocimiento: {e}")
        return False

def get_knowledge_base(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene el conocimiento del negocio, opcionalmente por categoría"""
    facts = []
    try:
        with get_cursor() as cur:
            if not cur: return []
            
            sql = "SELECT slug, category, content FROM business_knowledge"
            params = []
            if category:
                sql += " WHERE category = %s"
                params.append(category)
                
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            for row in rows:
                facts.append({
                    "slug": row[0],
                    "category": row[1],
                    "content": row[2]
                })
    except Exception as e:
        logger.error(f"❌ Error obteniendo knowledge base: {e}")
    return facts
