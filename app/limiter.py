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
# NOTE: Using 'storage_uri' allows slowapi to auto-connect to Redis.
limiter_storage = "memory://"

# In Vercel, we only use Redis if it's explicitly configured and NOT the default internal one
is_vercel = os.getenv("VERCEL") or os.getenv("RENDER")
default_redis = "redis://redis_evolution"

# 🛡️ Defensive Check: Ensure it's a real string (Protects against Test Mocks)
broker_url = settings.CELERY_BROKER_URL
if not isinstance(broker_url, str):
    broker_url = None

if broker_url and not (is_vercel and default_redis in broker_url):
    # Only use Redis for slowapi if it's external (e.g. Upstash)
    limiter_storage = broker_url
    logger.info(f"🌀 Rate Limiter using Redis storage: {limiter_storage.split('@')[-1]}")
else:
    logger.info("⚡ Rate Limiter using MEMORY storage (Optimized for Serverless Cold Start)")

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage)
