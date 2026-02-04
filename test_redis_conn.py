from upstash_redis import Redis

url = "https://concise-reindeer-45748.upstash.io"
token = "AbK0AAIncDI1OGQxZTUwMThiZjg0MDMxYjk4ZDliZDNlYzZiMjNjM3AyNDU3NDg"

print(f"Testing Upstash Redis connection to: {url}")

try:
    redis = Redis(url=url, token=token)
    ping_result = redis.ping()
    print(f"✅ Redis Ping Successful! Result: {ping_result}")
    
    # Test setting a key
    redis.set("test_agent_key", "alive", ex=60)
    val = redis.get("test_agent_key")
    print(f"✅ Redis Set/Get Successful! Value: {val}")
    
except Exception as e:
    print(f"❌ Redis Connection Failed: {e}")
