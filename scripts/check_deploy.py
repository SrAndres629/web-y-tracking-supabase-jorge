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

def check_vercel_config():
    print("📋 AUDITING VERCEL CONFIGURATION...")
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vercel.json')
    
    if not os.path.exists(config_path):
        print("⚠️  WARNING: vercel.json not found. Vercel will use default settings.")
        return

    import json
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 1. Check for legacy 'builds'
        if 'builds' in config:
            print("🟡 INFO: 'builds' property detected in vercel.json.")
            print("   Note: This overrides Vercel Project Settings in the UI (Legacy Mode).")
            print("   Vercel will ignore UI build settings for this project.")
            
            # 2. Verify source files exist
            for build in config.get('builds', []):
                src = build.get('src')
                if src and '*' not in src:
                    src_full = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), src)
                    if not os.path.exists(src_full):
                        print(f"❌ ERROR: Build source '{src}' does not exist!")
                        sys.exit(1)
                    else:
                        print(f"✅ Verified source: {src}")

        # 3. Check for 'functions' (Modern alternative)
        if 'functions' in config:
            print("✅ 'functions' property (Modern) detected.")

    except Exception as e:
        print(f"❌ Error parsing vercel.json: {e}")

def check_deploy():
    print("🛡️  INITIATING DEPLOYMENT SAFETY CHECK...")
    load_env()
    check_vercel_config()
    
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
