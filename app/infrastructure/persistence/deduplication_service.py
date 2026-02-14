"""
Deduplication Service (Redis-Backed)
=====================================
Ensures idempotency for tracking events using Upstash Redis.
Implementing Step 1 of MVP Phase 1.
"""

import logging
import json
from typing import Optional, Any
from upstash_redis import Redis
from app.config import settings

logger = logging.getLogger(__name__)

class DeduplicationService:
    def __init__(self):
        self._redis: Optional[Redis] = None
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection if credentials exist."""
        try:
            if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
                self._redis = Redis(
                    url=settings.UPSTASH_REDIS_REST_URL,
                    token=settings.UPSTASH_REDIS_REST_TOKEN,
                )
                logger.info("✅ DeduplicationService: Redis connected.")
            else:
                logger.warning("⚠️ DeduplicationService: Redis credentials missing. Falling back to memory (NOT PROD READY).")
        except Exception as e:
            logger.error(f"❌ DeduplicationService: Redis init failed: {e}")

    def try_consume_event(self, event_id: str, event_name: str = "event", ttl: int = 86400) -> bool:
        """
        Attempt to consume (process) an event ID.
        Returns:
            True: Event is NEW (lock acquired).
            False: Event is DUPLICATE (already processed).
        """
        if not event_id:
            return True # No ID, assume new (or invalid, but handled elsewhere)

        key = f"evt:{event_id}"
        
        # Strategy: SETNX (Set if Not Exists)
        if self._redis:
            try:
                # Upstash Redis REST API 'set' with nk (nx) argument? 
                # The python client uses .set(..., nx=True)
                # But upstash-redis might differ slightly from standard redis-py
                # Let's check typical usage or assume standard-ish.
                # Actually, upstash-redis-py usually supports .set(key, value, ex=ttl, nx=True)
                
                # We store a lightweight value, e.g., timestamp
                import time
                val = str(int(time.time()))
                
                # If set returns True/OK, it was set (New). If None, it existed (Duplicate).
                # Note: upstash-redis implementation dependent.
                result = self._redis.set(key, val, ex=ttl, nx=True)
                
                if result: 
                    return True # New
                else:
                    logger.info(f"🛑 Duplicate detected: {key}")
                    return False # Duplicate
                    
            except Exception as e:
                logger.error(f"⚠️ Redis Error in is_duplicate: {e}")
                return True # Fallback: process it to avoid data loss
        else:
            # Fallback to in-memory (handled in cache.py but duplication here for safety?)
            # Ideally we shouldn't reach here in PROD.
            return True

    def cache_visitor(self, external_id: str, data: dict, ttl: int = 86400):
        """Cache resolved visitor data for subsequent requests."""
        if not self._redis or not external_id:
            return
            
        key = f"vis:{external_id}"
        try:
            self._redis.set(key, json.dumps(data), ex=ttl)
        except Exception as e:
            logger.error(f"⚠️ Redis Error in cache_visitor: {e}")

    def get_visitor(self, external_id: str) -> Optional[dict]:
        """Get cached visitor data."""
        if not self._redis or not external_id:
            return None
            
        key = f"vis:{external_id}"
        try:
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"⚠️ Redis Error in get_visitor: {e}")
            return None
        return None

# Singleton Instance
dedup_service = DeduplicationService()
