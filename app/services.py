import os
import httpx
import logging

# Configure Logging
logger = logging.getLogger("uvicorn.error")

QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")
# Auto-detect Vercel URL or fallback to localhost for dev
VERCEL_URL = os.getenv("VERCEL_URL", "jorgeaguirreflores.com") 
if "http" not in VERCEL_URL:
    VERCEL_URL = f"https://{VERCEL_URL}"

async def publish_to_qstash(event_data: dict):
    """
    Publishes an event to QStash to be processed asynchronously.
    This bypasses Vercel's function freeze by offloading the work to an external queue.
    """
    if not QSTASH_TOKEN:
        logger.warning("⚠️ QStash Token missing! Falling back to direct execution (Risk of Freeze)")
        return False

    url = f"{VERCEL_URL}/api/hooks/process-event"
    
    headers = {
        "Authorization": f"Bearer {QSTASH_TOKEN}",
        "Content-Type": "application/json",
        "Upstash-Retries": "3" # Retry up to 3 times if our API is down
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://qstash.upstash.io/v2/publish/{url}",
                headers=headers,
                json=event_data,
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"🚀 Event offloaded to QStash: {response.json().get('messageId')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to publish to QStash: {str(e)}")
            return False
