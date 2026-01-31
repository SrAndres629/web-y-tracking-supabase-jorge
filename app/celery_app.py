# =================================================================
# CELERY APP CONFIGURATION
# Jorge Aguirre Flores Web
# =================================================================
import os
from celery import Celery
from app.config import settings

# 1. Detect Environment (Redis vs No-Redis)
# Determine if we should force Eager mode (No Redis)
FORCE_EAGER = False

# Check env var override
if os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() in ("true", "1", "yes"):
    FORCE_EAGER = True

# Check connectivity / Hostname validity
# If configured URL is the default docker internal one, but we likely aren't in that docker network (e.g. Render Web Service)
# we assume Redis is missing.
CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

if "redis_evolution" in CELERY_BROKER_URL:
     # In a real production environment with Redis, this hostname would be resolvable.
     # But on Render *Web Services*, standard Redis isn't there unless specified.
     # For safety, if we can't resolve it, we fallback.
     # However, DNS resolution might timeout. simpler: rely on FORCE_EAGER or explicit failure.
     # Current strategy: If user hasn't explicitly set a NEW broker url, and we are using the default "redis_evolution",
     # AND we are failing to connect (judging by logs), we should default to Memory.
     
     # To be safe and robust: If FORCE_EAGER is True, we MUST switch to InMemory broker/backend
     # to stop Celery from trying to connect to a dead Redis.
     pass

if FORCE_EAGER:
    # OVERRIDE CONNECTION STRINGS TO MEMORY
    # This prevents the "Connection to Redis lost: Retry" loop
    print("⚠️  Celery: Starting in EAGER mode (Memory Broker). Redis disabled.")
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://" 

celery_app = Celery(
    "jorge_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/La_Paz",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_always_eager=FORCE_EAGER
)

if FORCE_EAGER:
    print("⚠️  WARNING: Celery running in ALWAYS_EAGER mode (No Redis). Background tasks will block.")

if __name__ == "__main__":
    celery_app.start()
