# =================================================================
# CONSENT.PY - GDPR/CCPA/LGPD Compliance Endpoints
# =================================================================
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consent", tags=["privacy"])


class ConsentLogEntry(BaseModel):
    """Modelo de log de consentimiento para audit trail legal"""

    timestamp: str
    region: str
    consent: dict
    userAgent: str
    url: str
    ip: Optional[str] = None


@router.post("/log")
async def log_consent(request: Request):
    """
    Registra consentimiento del usuario para audit trail legal.
    Requerido por GDPR Art. 7 (prueba de consentimiento).
    """
    try:
        body = await request.json()

        # Agregar IP (anonimizada si es posible)
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host

        # Anonimizar IP (GDPR compliance)
        ip_parts = ip.split(".")
        if len(ip_parts) == 4:
            anonymized_ip = f"{ip_parts[0]}.{ip_parts[1]}.xxx.xxx"
        else:
            anonymized_ip = "anon"

        log_entry = {
            "timestamp": body.get("timestamp", datetime.utcnow().isoformat()),
            "region": body.get("region", "unknown"),
            "consent": body.get("consent", {}),
            "user_agent": body.get("userAgent", ""),
            "url": body.get("url", ""),
            "ip_hash": hash(anonymized_ip) % 10000,  # Hash parcial
            "user_id": request.cookies.get("external_id", "anonymous"),
        }

        # Guardar en archivo (producción: usar DB)
        from app.config import settings

        log_file = settings.BASE_DIR / ".logs" / "consent_audit.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        logger.info(f"✅ Consent logged for user {log_entry['user_id'][:16]}...")

        return JSONResponse(
            content={"status": "logged", "timestamp": log_entry["timestamp"]},
            headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
        )

    except Exception as e:
        logger.error(f"❌ Error logging consent: {e}")
        # No fallar el request del usuario
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.get("/status")
async def get_consent_status(request: Request):
    """
    Devuelve el estado de consentimiento del usuario actual.
    Útil para verificar antes de cargar scripts de tracking.
    """
    # Leer cookie de consentimiento
    consent_cookie = request.cookies.get("user_consent")

    if consent_cookie:
        try:
            consent = json.loads(consent_cookie)
            return {
                "has_consent": True,
                "consent": consent,
                "marketing_allowed": consent.get("marketing", False),
                "analytics_allowed": consent.get("analytics", False),
                "essential_allowed": True,  # Siempre true
            }
        except json.JSONDecodeError:
            pass

    return {
        "has_consent": False,
        "consent": None,
        "marketing_allowed": False,
        "analytics_allowed": False,
        "essential_allowed": True,
    }


@router.post("/withdraw")
async def withdraw_consent(request: Request):
    """
    Permite al usuario retirar consentimiento (GDPR Right to Withdraw).
    """
    try:
        # Limpiar cookies
        response = JSONResponse(
            {"status": "withdrawn", "message": "All consents have been withdrawn."}
        )

        # Expirar cookie de consentimiento
        response.delete_cookie(key="user_consent", path="/")

        # Log del retiro
        logger.info(
            f"🚫 Consent withdrawn for user {request.cookies.get('external_id', 'unknown')}"
        )

        return response

    except Exception as e:
        logger.error(f"❌ Error withdrawing consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
