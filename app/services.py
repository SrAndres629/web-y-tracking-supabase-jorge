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
async def validate_turnstile(token: str) -> bool:
    """
    Validates a Cloudflare Turnstile token.
    Shields the API from bot-generated tracking events.
    """
    if not settings.TURNSTILE_SECRET_KEY:
        logger.warning("🛡️ Turnstile Secret missing - bypassing validation (Insecure)")
        return True
    
    if not token:
        return False

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.TURNSTILE_SECRET_KEY,
                    "response": token
                },
                timeout=5.0
            )
            result = response.json()
            if result.get("success"):
                logger.info("🛡️ Turnstile validation successful")
                return True
            else:
                logger.warning(f"🛡️ Turnstile validation failed: {result.get('error-codes')}")
                return False
        except Exception as e:
            logger.error(f"🛡️ Turnstile verification error: {e}")
            return True # Fallback to true on network error to not block legit users
            
def normalize_pii(data: str, mode: str = "email") -> str:
    """
    Silicon Valley Hygiene: Clean and normalize PII before hashing.
    """
    if not data:
        return ""
    
    clean_data = data.strip().lower()
    
    if mode == "phone":
        # Keep only digits
        clean_data = "".join(filter(str.isdigit, data))
        # Ensure country code (default Bolivia 591 if 8 digits)
        if len(clean_data) == 8:
            clean_data = "591" + clean_data
            
    return clean_data

SERVICES_CONFIG = [
    {
        "id": "microblading",
        "title": "Microblading Elite",
        "description": "Cejas perfectas pelo a pelo con resultados naturales.",
        "icon": "fa-eye",
        "color": "luxury-gold"
    },
    {
        "id": "eyeliner",
        "title": "Delineado Permanente",
        "description": "Resalta tu mirada las 24 horas del día.",
        "icon": "fa-pencil",
        "color": "luxury-gold"
    },
    {
        "id": "lips",
        "title": "Acuarela de Labios",
        "description": "Color y definición vibrante para tus labios.",
        "icon": "fa-kiss",
        "color": "luxury-gold"
    }
]

CONTACT_CONFIG = {
    "whatsapp": "https://wa.me/59164714751",
    "phone": "+591 64714751",
    "email": "contacto@jorgeaguirreflores.com",
    "location": "Santa Cruz de la Sierra, Bolivia",
    "instagram": "https://instagram.com/jorgeaguirreflores"
}
