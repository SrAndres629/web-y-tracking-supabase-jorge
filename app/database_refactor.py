import logging
import sqlite3
from typing import Dict
import app.sql_queries as queries

# Mocking necessary imports for the standalone script check
try:
    import psycopg2
    from psycopg2.extensions import connection as PgConnection
except ImportError:
    class _MockPsycopg2:
        class Error(Exception): pass
    psycopg2 = _MockPsycopg2()
    class PgConnection: pass

DBConnection = sqlite3.Connection | PgConnection
DB_ERRORS = (sqlite3.Error, psycopg2.Error)
_backend = "sqlite"
logger = logging.getLogger(__name__)

def _create_cms_tables(conn: DBConnection) -> None:
    """Creates Site Content (CMS) tables."""
    try:
        cur = conn.cursor()
        cur.execute(queries.CREATE_TABLE_SITE_CONTENT)
        conn.commit()
    except DB_ERRORS:
        if conn:
            conn.rollback()

def _create_postgres_extensions(conn: DBConnection) -> None:
    """Creates PostGIS extension and custom types (Postgres only)."""
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

def _create_tenant_tables(conn: DBConnection, cf: Dict[str, str]) -> None:
    """Creates multi-tenant tables (clients, api_keys, emq_stats)."""
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
        except DB_ERRORS as e:
            if conn:
                conn.rollback()
            logger.warning("⚠️ Table creation skip/error (%s): %s", q_name, e)

def _run_client_migrations(conn: DBConnection) -> None:
    """Runs migrations for new columns in clients table."""
    try:
        cur = conn.cursor()
        cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS email TEXT UNIQUE")
        cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS company TEXT")
        conn.commit()
    except DB_ERRORS as e:
        if conn:
            conn.rollback()
        logger.warning("⚠️ Clients migration skip/error: %s", e)

def _create_business_tables(conn: DBConnection, cf: Dict[str, str]) -> None:
    """Creates Business Knowledge tables."""
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

def _create_visitor_tables(conn: DBConnection, cf: Dict[str, str]) -> None:
    """Creates Visitors tables."""
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

def _create_core_tables(cf: Dict[str, str]) -> None:
    # Note: get_db_connection is not mocked here so we assume conn is passed or handled differently in real code
    # But for the refactor, we are just defining the function structure.
    pass
