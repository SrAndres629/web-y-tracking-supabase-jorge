# =================================================================
# CACHE.PY - Redis Cache Layer for Event Deduplication (Upstash)
# Jorge Aguirre Flores Web
# =================================================================
# 
# PURPOSE: Ultra-fast event deduplication using Redis
# WHY: Postgres queries for deduplication are slow (50-200ms)
#      Redis checks are instant (<5ms), improving EMQ score
#
# SETUP: 
# 1. Create free account at https://upstash.com
# 2. Create Redis database (choose closest region: São Paulo)
# 3. Copy UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN
# 4. Add to Vercel Environment Variables
# =================================================================

import os
import logging
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

# Upstash Redis REST URL and Token
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

# Check if Redis is configured
REDIS_ENABLED = bool(UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN)

if REDIS_ENABLED:
    try:
        from upstash_redis import Redis
        redis_client = Redis(
            url=UPSTASH_REDIS_REST_URL,
            token=UPSTASH_REDIS_REST_TOKEN
        )
        logger.info("✅ Upstash Redis connected")
    except ImportError:
        logger.warning("⚠️ upstash-redis not installed. Run: pip install upstash-redis")
        REDIS_ENABLED = False
        redis_client = None
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        REDIS_ENABLED = False
        redis_client = None
else:
    redis_client = None
    logger.info("ℹ️ Redis not configured - using in-memory fallback")


# =================================================================
# IN-MEMORY FALLBACK (For local development)
# =================================================================
# Simple LRU-like cache for when Redis is not available
_memory_cache = {}
MAX_MEMORY_CACHE_SIZE = 10000


def _memory_set(key: str, value: str, ttl_seconds: int) -> bool:
    """In-memory fallback for Redis SET"""
    global _memory_cache
    
    # Simple size limit (no proper LRU, just clear if too big)
    if len(_memory_cache) > MAX_MEMORY_CACHE_SIZE:
        _memory_cache.clear()
    
    _memory_cache[key] = value
    return True


def _memory_get(key: str) -> Optional[str]:
    """In-memory fallback for Redis GET"""
    return _memory_cache.get(key)


def _memory_exists(key: str) -> bool:
    """In-memory fallback for Redis EXISTS"""
    return key in _memory_cache


# =================================================================
# PUBLIC API
# =================================================================

def is_duplicate_event(event_id: str, event_name: str = "event") -> bool:
    """
    Check if an event has already been processed.
    
    Args:
        event_id: Unique event identifier
        event_name: Event type for logging
        
    Returns:
        True if duplicate (already processed), False if new
    """
    cache_key = f"evt:{event_id}"
    
    if REDIS_ENABLED and redis_client:
        try:
            exists = redis_client.exists(cache_key)
            if exists:
                logger.debug(f"🔄 Duplicate {event_name} blocked: {event_id[:16]}...")
                return True
            return False
        except Exception as e:
            logger.warning(f"⚠️ Redis check failed, allowing event: {e}")
            return False  # Fail open - allow event if Redis fails
    else:
        return _memory_exists(cache_key)


def mark_event_processed(event_id: str, ttl_hours: int = 48) -> bool:
    """
    Mark an event as processed to prevent duplicates.
    
    Args:
        event_id: Unique event identifier
        ttl_hours: How long to remember the event (default 48h per Meta best practices)
        
    Returns:
        True if marked successfully
    """
    cache_key = f"evt:{event_id}"
    ttl_seconds = ttl_hours * 3600
    
    if REDIS_ENABLED and redis_client:
        try:
            redis_client.set(cache_key, "1", ex=ttl_seconds)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis set failed: {e}")
            return _memory_set(cache_key, "1", ttl_seconds)
    else:
        return _memory_set(cache_key, "1", ttl_seconds)


def deduplicate_event(event_id: str, event_name: str = "event") -> bool:
    """
    Combined check-and-mark for event deduplication.
    
    Args:
        event_id: Unique event identifier
        event_name: Event type for logging
        
    Returns:
        True if event should be processed (new event)
        False if event should be skipped (duplicate)
    """
    if is_duplicate_event(event_id, event_name):
        return False  # Skip duplicate
    
    mark_event_processed(event_id)
    return True  # Process new event


# =================================================================
# RATE LIMITING (Bonus Feature)
# =================================================================

def check_rate_limit(identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    """
    Simple rate limiting using Redis.
    
    Args:
        identifier: User identifier (IP, user_id, etc.)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Returns:
        True if request is allowed, False if rate limited
    """
    if not REDIS_ENABLED or not redis_client:
        return True  # No rate limiting without Redis
    
    rate_key = f"rate:{identifier}"
    
    try:
        current = redis_client.get(rate_key)
        
        if current is None:
            redis_client.set(rate_key, "1", ex=window_seconds)
            return True
        
        count = int(current)
        if count >= max_requests:
            logger.warning(f"🚫 Rate limit exceeded for {identifier[:16]}...")
            return False
        
        redis_client.incr(rate_key)
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Rate limit check failed: {e}")
        return True  # Fail open


# =================================================================
# VISITOR SESSION CACHE (For EMQ Boost)
# =================================================================

def cache_visitor_data(external_id: str, data: dict, ttl_hours: int = 24) -> bool:
    """
    Cache visitor data for quick retrieval (fbclid, fbp, etc.)
    Avoids hitting Postgres on every request.
    """
    cache_key = f"visitor:{external_id}"
    ttl_seconds = ttl_hours * 3600
    
    if REDIS_ENABLED and redis_client:
        try:
            import json
            redis_client.set(cache_key, json.dumps(data), ex=ttl_seconds)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Visitor cache failed: {e}")
            return False
    return False


def get_cached_visitor(external_id: str) -> Optional[dict]:
    """
    Retrieve cached visitor data.
    """
    cache_key = f"visitor:{external_id}"
    
    if REDIS_ENABLED and redis_client:
        try:
            import json
            data = redis_client.get(cache_key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"⚠️ Visitor cache get failed: {e}")
    return None


# =================================================================
# HEALTH CHECK
# =================================================================

def redis_health_check() -> dict:
    """Check Redis connection health."""
    if not REDIS_ENABLED:
        return {"status": "disabled", "message": "Redis not configured"}
    
    try:
        redis_client.ping()
        return {"status": "healthy", "provider": "upstash"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
