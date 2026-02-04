import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# The production string I set
db_url = "postgresql://postgres.eycumxvxyqzznjkwaumx:Omegated669!@aws-0-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require"

print(f"Testing connection to: {db_url.split('@')[1]}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    record = cur.fetchone()
    print("✅ Connection successful!")
    print(f"Database version: {record}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
