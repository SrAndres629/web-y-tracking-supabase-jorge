# =================================================================
# RETRY_QUEUE.PY - Meta CAPI Resilience Logic (Redis DLQ)
# Jorge Aguirre Flores Web
# =================================================================
import json
import logging
import time
from typing import Any, Dict, Optional

from app.infrastructure.cache.redis_provider import redis_provider
from app.infrastructure.config.settings import settings

logger = logging.getLogger("DistQueue")

# 🔒 CONSTANTS
DLQ_KEY = "meta_capi:dlq"
MAX_RETRIES = 5
RETRY_BACKOFF_BASE = 300  # 5 minutes


class RedisDLQ:
    """Dead Letter Queue backed by the shared RedisProvider."""

    @property
    def _redis(self):
        return redis_provider.sync_client

    def push(self, event_name: str, payload: Dict[str, Any], attempt: int = 1):
        """Push a failed event to the Redis DLQ"""
        if not self._redis:
            logger.warning(f"⚠️ [DLQ] Redis unavailable. Event '{event_name}' lost.")
            return

        item = {
            "event_name": event_name,
            "payload": payload,
            "failed_at": int(time.time()),
            "attempt": attempt,
            "next_retry": int(time.time()) + (RETRY_BACKOFF_BASE * (2 ** (attempt - 1))),
        }

        try:
            self._redis.rpush(DLQ_KEY, json.dumps(item))
            logger.info(
                f"📥 [DLQ] Saved '{event_name}' for retry #{attempt} (Next: +{item['next_retry'] - int(time.time())}s)"
            )
        except Exception as e:
            logger.exception(f"❌ [DLQ] Failed to save event: {e}")

    def pop_batch(self, batch_size: int = 10) -> list:
        """Atomic fetch of pending items (simulated with LPOP)"""
        if not self._redis:
            return []

        items = []
        try:
            for _ in range(batch_size):
                raw = self._redis.lpop(DLQ_KEY)
                if not raw:
                    break
                content = raw[0] if isinstance(raw, list) else raw
                items.append(json.loads(content))
        except Exception as e:
            logger.exception(f"❌ [DLQ] Fetch error: {e}")

        return items


# Singleton
dlq = RedisDLQ()


def add_to_retry_queue(event_name: str, payload: Dict[str, Any]):
    """Public interface to add events to DLQ"""
    logger.warning(f"⚠️ [CAPI FAIL] Adding '{event_name}' to Redis DLQ...")
    dlq.push(event_name, payload)


async def process_retry_queue(batch_size: int = 20):
    """
    Background Task: Process pending retries
    Resolves items that are due for retry. Re-queues those that aren't ready.
    """
    if not dlq._redis:
        return

    items = dlq.pop_batch(batch_size)
    if not items:
        return

    logger.info(f"🔄 [DLQ] Processing {len(items)} events from Redis...")

    # We need to import here to avoid circular dependencies
    from app.tracking import EnhancedCustomData, EnhancedUserData, elite_capi

    requeued_count: int = 0
    success_count: int = 0
    drop_count: int = 0

    now: int = int(time.time())

    for item in items:
        if item["next_retry"] > now:
            dlq.push(item["event_name"], item["payload"], item["attempt"])
            requeued_count += 1
            continue

        event_name = item["event_name"]
        payload = item["payload"]
        attempt = item["attempt"]

        logger.info(f"✨ [DLQ] Retrying '{event_name}' (Attempt {attempt}/{MAX_RETRIES})...")

        try:
            user_data_raw = payload.get("user_data", {})
            custom_data_raw = payload.get("custom_data", {})

            user_data = EnhancedUserData(**user_data_raw)
            custom_data = EnhancedCustomData(**custom_data_raw) if custom_data_raw else None

            result = await elite_capi.send_event(
                event_name=event_name,
                event_id=payload.get("event_id"),
                event_source_url=payload.get("event_source_url") or payload.get("url"),
                user_data=user_data,
                custom_data=custom_data,
                client_ip=payload.get("client_ip"),
                user_agent=payload.get("user_agent"),
            )

            status = result.get("status")
            if status in ["success", "duplicate", "sandbox"]:
                logger.info(f"✅ [DLQ] Success: '{event_name}' recovered.")
                success_count += 1
            else:
                raise Exception(f"API Returned {status}")

        except Exception as e:
            logger.warning(f"⚠️ [DLQ] Validation/Send Error: {e}")

            if attempt < MAX_RETRIES:
                dlq.push(event_name, payload, attempt + 1)
                requeued_count += 1
            else:
                logger.exception(f"🗑️ [DLQ] Dropping '{event_name}' after {MAX_RETRIES} attempts.")
                drop_count += 1

    if success_count > 0:
        logger.info(
            f"🏁 [DLQ] Batch Complete. Recovered: {success_count}, Re-queued: {requeued_count}, Dropped: {drop_count}"
        )
