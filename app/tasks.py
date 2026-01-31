# =================================================================
# CELERY TASKS - Web & Tracking Only
# Jorge Aguirre Flores Web
# =================================================================
from app.celery_app import celery_app
from app.tracking import send_event, send_n8n_webhook
from app.database import save_visitor
import logging

logger = logging.getLogger("worker")

# =================================================================
# DATABASE TASKS
# =================================================================

@celery_app.task(bind=True, name="save_visitor_task", default_retry_delay=5, max_retries=3)
def save_visitor_task(self, external_id, fbclid, client_ip, user_agent, source, utm_data):
    """Persist visitor data to DB asynchronously"""
    try:
        save_visitor(
            external_id=external_id,
            fbclid=fbclid,
            ip_address=client_ip,
            user_agent=user_agent,
            source=source,
            utm_data=utm_data
        )
        logger.info(f"✅ Visitor saved: {external_id}")
    except Exception as e:
        logger.error(f"❌ Error saving visitor: {e}")
        raise self.retry(exc=e)

# =================================================================
# EXTERNAL API TASKS
# =================================================================

@celery_app.task(bind=True, name="send_meta_event_task", default_retry_delay=5, max_retries=3)
def send_meta_event_task(self, event_name, event_source_url, client_ip, user_agent, event_id, fbclid=None, fbp=None, external_id=None, phone=None, email=None, custom_data=None):
    """Send event to Facebook Conversions API"""
    try:
        success = send_event(
            event_name=event_name,
            event_source_url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            event_id=event_id,
            fbclid=fbclid,
            fbp=fbp,
            external_id=external_id,
            phone=phone,
            email=email,
            custom_data=custom_data
        )
        if not success:
            raise Exception("Meta API returned failure")
        logger.info(f"✅ Meta Event sent: {event_name}")
    except Exception as e:
        logger.warning(f"⚠️ Meta send failed (retrying): {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="send_n8n_webhook_task", default_retry_delay=5, max_retries=5)
def send_n8n_webhook_task(self, payload):
    """Send webhook to n8n"""
    try:
        success = send_n8n_webhook(payload)
        if not success:
            raise Exception("n8n Webhook failed")
        logger.info("✅ n8n Webhook sent")
    except Exception as e:
        logger.warning(f"⚠️ n8n send failed (retrying): {e}")
        raise self.retry(exc=e)
