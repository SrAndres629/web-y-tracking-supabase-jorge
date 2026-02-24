# =================================================================
# LIMITER.PY - Shared Rate Limiter Instance
# =================================================================
import logging
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

logger = logging.getLogger(__name__)

# Check for Redis URL (Upstash or Local)
# NOTE: slowapi requires redis:// or rediss:// scheme — Upstash REST (https://) won't work.
limiter_storage = "memory://"

# In Vercel serverless, each invocation is stateless so memory is fine.
is_vercel = os.getenv("VERCEL") or os.getenv("RENDER")

# 🛡️ Defensive Check: Only use Redis if it has a valid redis:// or rediss:// scheme
# Compatibility chain:
# 1) Legacy CELERY_BROKER_URL (if still present)
# 2) Flat REDIS_URL from new settings
# 3) Nested redis.url from new settings
broker_url = (
    getattr(settings, "CELERY_BROKER_URL", None)
    or getattr(settings, "REDIS_URL", None)
    or getattr(getattr(settings, "redis", None), "url", None)
)
if (
    isinstance(broker_url, str)
    and broker_url.startswith(("redis://", "rediss://"))
    and "upstash.io" in broker_url
):
    # Only use Redis for slowapi if it's a proper Redis protocol connection
    limiter_storage = broker_url
    logger.info(f"🌀 Rate Limiter using Redis storage: {limiter_storage.split('@')[-1]}")
elif isinstance(broker_url, str) and broker_url.startswith("https://"):
    logger.warning(
        "⚠️ Rate Limiter: Upstash REST URL detected. Falling back to MEMORY (REST not supported by slowapi)."
    )
    limiter_storage = "memory://"
else:
    logger.info("⚡ Rate Limiter using MEMORY storage (No valid Redis URI or Serverless)")

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage)
