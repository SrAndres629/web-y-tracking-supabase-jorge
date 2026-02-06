# =================================================================
# MAINTENANCE.PY - El Recolector de Basura (Garbage Collector)
# Jorge Aguirre Flores Web
# =================================================================
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_cursor
from app.config import settings

router = APIRouter(prefix="/maintenance", tags=["System"])
logger = logging.getLogger(__name__)

def verify_cron_secret(request: Request):
    """
    Verifica que la petición venga del Cron de Vercel
    Header: 'Authorization: Bearer <CRON_SECRET>'
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {settings.ADMIN_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized Cron Access")
    return True

@router.get("/clean_garbage_data")
async def clean_garbage_data(authorized: bool = Depends(verify_cron_secret)):
    """
    🧹 GARBAGE COLLECTOR (Silicon Valley Hygiene)
    Elimina registros 'basura' (Visitors sin lead) de más de 90 días.
    Mantiene la BD ligera y la API rápida.
    """
    try:
        deleted_count = 0
        with get_cursor() as cur:
            # PostgreSQL logic for date arithmetic
            # visitors table usually has 'timestamp' or 'created_at' column
            # We assume 'timestamp' based on previous analysis
            
            query = """
                DELETE FROM visitors 
                WHERE timestamp < NOW() - INTERVAL '90 days'
                AND external_id NOT IN (SELECT fb_browser_id FROM contacts WHERE fb_browser_id IS NOT NULL)
            """
            
            # Adjust for SQLite if running locally (fallback)
            if settings.DATABASE_URL is None or "sqlite" in settings.DATABASE_URL:
                 query = "DELETE FROM visitors WHERE timestamp < date('now', '-90 days')"

            cur.execute(query)
            deleted_count = cur.rowcount
            
        logger.info(f"🧹 Garbage Collector Run: Defeated {deleted_count} stale rows.")
        return {"status": "success", "rows_deleted": deleted_count, "message": "Database hygiene check complete."}
        
    except Exception as e:
        logger.error(f"❌ Garbage Collector Failed: {e}")
        return {"status": "error", "message": str(e)}
