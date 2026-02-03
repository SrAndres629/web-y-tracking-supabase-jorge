import os
import sys
import time
import urllib.parse
from dotenv import load_dotenv
import psycopg2

# Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def log(message, color=RESET):
    print(f"{color}{message}{RESET}")

def verify_environment():
    log("🔍 Starting Environment Diagnostic Probe...", GREEN)
    
    # 1. Load Environment
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        log("❌ CRITICAL: DATABASE_URL not found in environment.", RED)
        sys.exit(1)
        
    log(f"✅ DATABASE_URL found.", GREEN)

    # Mask password for logging
    try:
        parsed = urllib.parse.urlparse(db_url)
        masked_url = db_url.replace(parsed.password, "******") if parsed.password else db_url
        log(f"ℹ️  Connection String: {masked_url}")
        
        # 2. Check Port (The Transaction Pooler Check)
        port = parsed.port
        if port == 6543:
            log("✅ Port 6543 detected (Supabase Transaction Pooler).", GREEN)
        elif port == 5432:
            log("⚠️  WARNING: Port 5432 detected (Session Mode).", YELLOW)
            log("   -> In a Serverless environment (Vercel), this creates a risk of connection exhaustion.", YELLOW)
            log("   -> RECOMMENDATION: Change port to 6543.", YELLOW)
        else:
            log(f"ℹ️  Port {port} detected.", YELLOW)
            
        # 3. Connection Test
        log("Testing connection latency (SELECT 1)...")
        start_time = time.time()
        
        try:
            conn = psycopg2.connect(db_url)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                
            elapsed = (time.time() - start_time) * 1000
            conn.close()
            
            if result and result[0] == 1:
                color = GREEN if elapsed < 500 else YELLOW
                log(f"✅ Connection Successful! Latency: {elapsed:.2f}ms", color)
            else:
                log("❌ Connection established but unexpected result.", RED)
                
        except Exception as e:
            log(f"❌ Connection Failed: {e}", RED)
            sys.exit(1)
            
    except Exception as e:
        log(f"❌ Error parsing URL or generic failure: {e}", RED)
        sys.exit(1)

if __name__ == "__main__":
    verify_environment()
