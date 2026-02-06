# =================================================================
# LIMITER.PY - Shared Rate Limiter Instance
# =================================================================
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Check for Redis URL (Upstash or Local)
# NOTE: Using 'storage_uri' allows slowapi to auto-connect to Redis.
limiter_storage = "memory://"
if settings.UPSTASH_REDIS_REST_URL:
    # Convert REST URL to Standard Redis URL if possible, or fallback to memory if using HTTP-only
    # For slowapi, we need a standard redis:// connection string. 
    # Usually provided via REDIS_URL or CELERY_BROKER_URL in our config.
    if settings.CELERY_BROKER_URL:
        limiter_storage = settings.CELERY_BROKER_URL
    else:
        logger.warning("⚠️ Rate Limiter using MEMORY storage (Not safe for serverless scaling)")

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage)
