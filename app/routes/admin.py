# =================================================================
# ADMIN.PY - Panel de Administración
# Jorge Aguirre Flores Web
# =================================================================
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models import ConfirmSaleResponse, ErrorResponse
from app.database import get_all_visitors, get_visitor_by_id
from app.tasks import send_meta_event_task

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


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


@router.post("/confirm/{visitor_id}")
async def confirm_sale(visitor_id: int, key: str = ""):
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
    send_meta_event_task.delay(
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
