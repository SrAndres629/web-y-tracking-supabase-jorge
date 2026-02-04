import os
import sys
from dotenv import load_dotenv
try:
    from upstash_redis import Redis
except ImportError:
    print("❌ upstash-redis package not found. Run: pip install upstash-redis")
    sys.exit(1)

def verify_redis():
    print("🔍 Testing Upstash Redis Connection...")
    load_dotenv()
    
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    if not url or not token:
        print("❌ Missing UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN in .env")
        sys.exit(1)
        
    print(f"ℹ️  URL: {url}")
    
    try:
        redis = Redis(url=url, token=token)
        # Test Write
        redis.set("elite_verifier", "success")
        # Test Read
        val = redis.get("elite_verifier")
        
        if val == "success":
            print("✅ Redis Connection Successful! (Read/Write confirmed)")
        else:
            print(f"⚠️  Redis connected but returned unexpected value: {val}")
            
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_redis()
