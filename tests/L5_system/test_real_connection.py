import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

from importlib import reload

# 🛡️ SILICON VALLEY STRICT AUDIT
# This test bypasses standard fixtures to verify REAL infrastructure.


def test_real_database_connection():
    """
    Verifies that the application can actually connect to the database
    defined in the environment, bypassing unit test mocks.
    """
    print("\n🕵️ STARTING STRICT DATABASE AUDIT...")

    # 1. Force reload of configuration to pick up REAL .env (not mocks)
    # We must unset mocking env vars if they were set by conftest (though this runs in a separate process usually)
    if "DATABASE_URL" in os.environ and "sqlite" in os.environ["DATABASE_URL"]:
        print(
            "⚠️ WARNING: DATABASE_URL points to SQLite. Ensure this is intended for this environment."
        )

    # Reload modules to clear any cached mock states
    import app.config

    reload(app.config)
    import app.database

    reload(app.database)

    from app.config import settings
    from app.database import BACKEND, check_connection, get_db_connection

    print(f"   👉 Backend Constraint: {BACKEND}")
    print(f"Status: {settings.DATABASE_URL}")
    print(f"   👉 DSN Configured: {(settings.DATABASE_URL or '')[:15]}... (Masked)")

    # 2. Check Connection
    is_connected = check_connection()

    if not is_connected:
        print("   ❌ CONNECTION FAILED: check_connection() returned False.")

        # Diagnostics
        if BACKEND == "postgres":
            import psycopg2

            try:
                conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=3)
                conn.close()
                print("   ❓ Weird: Raw psycopg2 connection WORKED, but app logic failed.")
            except Exception as e:
                print(f"   🔥 Raw Connection Diagnostics: {e}")
    else:
        print("   ✅ CONNECTION SUCCESSFUL: Database is reachable.")

    # 3. Verify Table Existence (Readiness)
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM visitors")
            count = cur.fetchone()[0]
            print(f"   ✅ SCHEMA VERIFIED: 'visitors' table exists (Rows: {count})")
    except Exception as e:
        print(f"   ❌ SCHEMA ERROR: Could not query 'visitors' table. {e}")
        is_connected = False

    assert is_connected, "Complete Database Handshake Failed"


if __name__ == "__main__":
    # Allow running directly: python tests/backend/strict_audit/test_real_connection.py
    try:
        test_real_database_connection()
        print("\n✨ AUDIT PASSED")
    except AssertionError as e:
        print(f"\n🚫 AUDIT FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 AUDIT CRASHED: {e}")
        sys.exit(1)
