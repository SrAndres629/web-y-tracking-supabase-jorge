from upstash_redis import Redis
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url = os.getenv("UPSTASH_REDIS_REST_URL", "https://concise-reindeer-45748.upstash.io")
token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

logger.info(f"Testing Upstash Redis connection to: {url}")

try:
    redis = Redis(url=url, token=token)
    ping_result = redis.ping()
    logger.info(f"✅ Redis Ping Successful! Result: {ping_result}")
    
    # Test setting a key
    redis.set("test_agent_key", "alive", ex=60)
    val = redis.get("test_agent_key")
    logger.info(f"✅ Redis Set/Get Successful! Value: {val}")
    
except Exception as e:
    logger.error(f"❌ Redis Connection Failed: {e}")
