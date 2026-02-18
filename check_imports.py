import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    import app.sql_queries

    print("✅ app.sql_queries imported successfully")
except ImportError as e:
    print(f"❌ app.sql_queries failed: {e}")

try:
    from app.config import settings

    _ = settings
    print("✅ app.config settings imported successfully")
except ImportError as e:
    print(f"❌ app.config settings failed: {e}")

try:
    import app.infrastructure.persistence.database

    _ = app.infrastructure.persistence.database
    print("✅ app.infrastructure.persistence.database imported successfully")
except ImportError as e:
    print(f"❌ app.infrastructure.persistence.database failed: {e}")

print("sys.path:", sys.path)
