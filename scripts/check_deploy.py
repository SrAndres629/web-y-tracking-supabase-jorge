import os
import sys
import psycopg2

# Simple .env loader to avoid external dependency if not installed
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        print(f"📄 Loading .env from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
    else:
        print("⚠️ No .env file found (checking system env vars)")

def check_deploy():
    print("🛡️  INITIATING DEPLOYMENT SAFETY CHECK...")
    load_env()
    
    # 1. Check Critical Env Vars
    required_vars = ["DATABASE_URL", "META_PIXEL_ID", "META_ACCESS_TOKEN"]
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
        else:
            # Hide secret values in logs
            val = os.environ.get(var)
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "****"
            print(f"✅ Found {var}: {masked}")
            
    if missing:
        print(f"❌ CRITICAL ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
        
    # 2. Database Connectivity Ping
    db_url = os.environ.get("DATABASE_URL")
    print(f"🔌 Testing Database Connection...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print("✅ DB Connected Successfully (PostgreSQL)")
    except Exception as e:
        print(f"❌ DB Error: Could not connect to PostgreSQL.")
        print(f"   Details: {str(e)}")
        sys.exit(1)

    print("🚀 PRE-FLIGHT CHECK PASSED. SYSTEM SECURE FOR DEPLOY.")

if __name__ == "__main__":
    check_deploy()
