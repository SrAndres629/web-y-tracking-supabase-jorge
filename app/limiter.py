# =================================================================
# LIMITER.PY - Shared Rate Limiter Instance
# =================================================================
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Check for Redis URL (Upstash or Local)
# NOTE: Using 'storage_uri' allows slowapi to auto-connect to Redis.
limiter_storage = "memory://"

# In Vercel, we only use Redis if it's explicitly configured and NOT the default internal one
is_vercel = os.getenv("VERCEL") or os.getenv("RENDER")
default_redis = "redis://redis_evolution"

if settings.CELERY_BROKER_URL and not (is_vercel and default_redis in settings.CELERY_BROKER_URL):
    # Only use Redis for slowapi if it's external (e.g. Upstash)
    limiter_storage = settings.CELERY_BROKER_URL
    logger.info(f"🌀 Rate Limiter using Redis storage: {limiter_storage.split('@')[-1]}")
else:
    logger.info("⚡ Rate Limiter using MEMORY storage (Optimized for Serverless Cold Start)")

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage)
