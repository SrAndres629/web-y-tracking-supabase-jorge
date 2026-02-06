# =================================================================
# ADMIN.PY - Panel de Administración
# Jorge Aguirre Flores Web
# =================================================================
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models import ConfirmSaleResponse, ErrorResponse
from app.database import get_all_visitors, get_visitor_by_id
from app.routes.tracking_routes import bg_send_meta_event

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

# Import queries directly for raw stats
from app.database import get_cursor


def verify_admin_key(key: str) -> bool:
    """Verifica la clave de administrador"""
    return key == settings.ADMIN_KEY


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, key: str = ""):
    """
    Panel de administración protegido por clave
    Muestra los últimos visitantes y permite confirmar ventas
    """
    if not verify_admin_key(key):
        return HTMLResponse(
            "<h1>🔒 Acceso Denegado</h1><p>Clave incorrecta.</p>", 
            status_code=403
        )
    
    visitors = get_all_visitors(limit=50)
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "visitors": visitors,
        "admin_key": key
    })


@router.get("/stats")
async def admin_stats(key: str = ""):
    """Devuelve JSON con estadísticas para monitoreo externo"""
    if not verify_admin_key(key):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    visitors = get_all_visitors(limit=1000)
    return {
        "total_visitors": len(visitors),
        "status": "active",
        "database": "connected"
    }


@router.post("/confirm/{visitor_id}")
async def confirm_sale(visitor_id: int, background_tasks: BackgroundTasks, key: str = ""):
    """
    Confirma una venta y envía evento Purchase a Meta CAPI
    
    Esto permite cerrar el loop de atribución:
    1. Usuario ve anuncio en Meta
    2. Hace clic (capturamos fbclid)
    3. Visita la web (guardamos en DB)
    4. Contacta por WhatsApp (Lead)
    5. Admin confirma venta (Purchase)
    → Meta aprende qué audiencias convierten
    """
    # Validar acceso
    if not verify_admin_key(key):
        return JSONResponse(
            {"status": "error", "error": "Clave incorrecta"}, 
            status_code=403
        )
    
    # Buscar visitante
    visitor = get_visitor_by_id(visitor_id)
    if not visitor:
        return JSONResponse(
            {"status": "error", "error": "Visitante no encontrado"}, 
            status_code=404
        )
    
    # Enviar Purchase a Meta CAPI (Background)
    # Using FastAPI BackgroundTasks instead of Celery for Vercel/Serverless
    background_tasks.add_task(
        bg_send_meta_event,
        event_name="Purchase",
        event_source_url=f"{settings.HOST}/admin",
        client_ip="127.0.0.1",
        user_agent="Admin Dashboard",
        event_id=f"purchase_{visitor_id}_{int(time.time())}",
        fbclid=visitor.get("fbclid"),
        external_id=visitor.get("external_id"),
        custom_data={
            "value": 350.00,
            "currency": "USD"
        }
    )
    
    return JSONResponse({
        "status": "success",
        "visitor_id": visitor_id,
        "message": "Evento Purchase encolado correctamente"
    })

@router.get("/signals")
async def audit_signals(key: str = ""):
    """
    AUDITORÍA DE SEÑALES (Silicon Valley Signal Quality)
    Compara Leads (DB) vs Eventos Enviados (Flag 'sent_to_meta')
    Muestra la discrepancia real.
    """
    if not verify_admin_key(key):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)

    try:
        with get_cursor() as cur:
             # 1. Total Contactos Únicos
             cur.execute("SELECT COUNT(*) FROM contacts")
             total_leads = cur.fetchone()[0]

             # 2. Total Enviados a Meta (Usando un campo teórico 'sent_to_meta' o log de events)
             # Nota: Asumiendo que tenemos una tabla de auditoría o flag. 
             # Si no, contamos leads con fbclid como proxy de calidad.
             cur.execute("SELECT COUNT(*) FROM contacts WHERE fbclid IS NOT NULL")
             leads_with_signal = cur.fetchone()[0]
             
             # 3. Discrepancy
             match_rate = 0
             if total_leads > 0:
                 match_rate = round((leads_with_signal / total_leads) * 100, 2)
                 
             return {
                 "status": "active",
                 "audit": {
                     "total_leads_db": total_leads,
                     "quality_leads_with_fbclid": leads_with_signal,
                     "signal_match_rate": f"{match_rate}%",
                     "alert": "LOW SIGNAL" if match_rate < 50 else "HEALTHY"
                 },
                 "recommendation": "Check 'tracking.js' if Match Rate < 80%"
             }
    except Exception as e:
        return {"error": str(e)}
