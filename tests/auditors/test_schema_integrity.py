import pytest
import logging
from app.database import get_db_connection, BACKEND

logger = logging.getLogger(__name__)

def test_database_schema_integrity():
    """
    🛡️ ARCHITECTURAL AUDIT: Schema Integrity
    Verifies that the live database contains ALL columns required by the application code.
    This prevents 'Column does not exist' 500 errors during deployments.
    """
    required_columns = {
        "contacts": [
            "profile_pic_url", "fb_browser_id", "utm_term", "utm_content", 
            "status", "lead_score", "pain_point", "service_interest", 
            "service_booked_date", "appointment_count", "updated_at", 
            "onboarding_step", "is_admin"
        ],
        "visitors": [
            "fbclid", "utm_content", "ip", "user_agent"
        ]
    }

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for table, columns in required_columns.items():
            # Get actual columns from DB
            if BACKEND == "postgres":
                # Postgres introspection
                try:
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
                    existing_columns = {row[0] for row in cursor.fetchall()}
                except Exception as e:
                     pytest.fail(f"❌ Postgres Audit Failed for table '{table}': {e}. (Hint: Run migrations or check DATABASE_URL)")
            else:
                # SQLite introspection
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    rows = cursor.fetchall()
                    # SQLite returns (cid, name, type, notnull, dflt_value, pk)
                    existing_columns = {row[1] for row in rows}
                except Exception as e:
                    pytest.fail(f"❌ Could not inspect SQLite table {table}: {e}")

            # Verify EACH required column exists
            missing = []
            for col in columns:
                if col not in existing_columns:
                    missing.append(col)
            
            if missing:
                pytest.fail(f"🔥 SCHEMA VIOLATION: Table '{table}' is missing columns: {missing}. Run migrations!")
            else:
                logger.info(f"✅ Table '{table}' schema is valid.")
