# =================================================================
# MAINTENANCE.PY - El Recolector de Basura (Garbage Collector)
# Jorge Aguirre Flores Web
# =================================================================
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.infrastructure.persistence.database import db
from app.infrastructure.config.settings import settings

router = APIRouter(prefix="/maintenance", tags=["System"])
logger = logging.getLogger(__name__)


def verify_cron_secret(request: Request):
    """
    Verifica que la petición venga del Cron de Vercel
    Header: 'Authorization: Bearer <CRON_SECRET>'
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {settings.ADMIN_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized Cron Access")
    return True


@router.get("/clean_garbage_data")
async def clean_garbage_data(_authorized: bool = Depends(verify_cron_secret)):
    """
    🧹 GARBAGE COLLECTOR (Silicon Valley Hygiene)
    Elimina registros 'basura' (Visitors sin lead) de más de 90 días.
    Mantiene la BD ligera y la API rápida.
    """
    try:
        deleted_count = 0
        async with db.connection() as conn:
            cur = conn.cursor()
            # PostgreSQL logic for date arithmetic
            query = """
                DELETE FROM visitors
                WHERE created_at < NOW() - INTERVAL '90 days'
                AND external_id NOT IN (SELECT external_id FROM leads WHERE external_id IS NOT NULL)
            """

            # Adjust for SQLite if running locally (fallback)
            if db.backend == "sqlite":
                query = """
                    DELETE FROM visitors 
                    WHERE created_at < date('now', '-90 days')
                    AND external_id NOT IN (SELECT external_id FROM leads WHERE external_id IS NOT NULL)
                """

            cur.execute(query)
            deleted_count = cur.rowcount

        logger.info(f"🧹 Garbage Collector Run: Defeated {deleted_count} stale rows.")
        return {
            "status": "success",
            "rows_deleted": deleted_count,
            "message": "Database hygiene check complete.",
        }

    except Exception as e:
        logger.exception(f"❌ Garbage Collector Failed: {e}")
        return {"status": "error", "message": str(e)}
