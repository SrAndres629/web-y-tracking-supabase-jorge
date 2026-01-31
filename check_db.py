import sqlite3
import os

def check_tables():
    db_path = os.path.join('database', 'local_fallback.db')
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print("Detected Tables:", tables)
    conn.close()

if __name__ == "__main__":
    check_tables()
