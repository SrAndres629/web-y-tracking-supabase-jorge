import secrets
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from app.application.commands.admin.confirm_sale_command import ConfirmSaleCommand
from app.application.queries.admin.get_all_visitors_query import GetAllVisitorsQuery
from app.application.queries.admin.get_signal_audit_query import GetSignalAuditQuery
from app.config import settings
from app.interfaces.api.dependencies import get_legacy_facade

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRS)
legacy = get_legacy_facade()


security = HTTPBasic(auto_error=False)


async def validate_admin_access(
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
):
    """
    Valida el acceso de administrador mediante:
    1. Header 'X-Admin-Key'
    2. HTTP Basic Auth (usando la clave como password)
    """
    # 1. Validar por Header (Ideal para APIs)
    if x_admin_key and secrets.compare_digest(x_admin_key, settings.ADMIN_KEY):
        return True

    # 2. Validar por Basic Auth (Ideal para navegación en navegador)
    if credentials and secrets.compare_digest(credentials.password, settings.ADMIN_KEY):
        return True

    # Si ninguno es válido, lanzar 401 para activar el prompt del navegador
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="🔒 Acceso Denegado",
        headers={"WWW-Authenticate": "Basic"},
    )


def verify_admin_key(key: str) -> bool:
    """
    Verifica la clave de administrador (Legacy support)
    DEPRECATED: Use validate_admin_access dependency instead.
    """
    return secrets.compare_digest(key, settings.ADMIN_KEY)


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _=Depends(validate_admin_access)):
    """
    Panel de administración protegido por clave
    Muestra los últimos visitantes y permite confirmar ventas
    """
    get_visitors_query = GetAllVisitorsQuery(list_visitors=legacy.get_all_visitors)
    visitors = await get_visitors_query.execute(limit=50)

    from app.database import get_emq_stats

    emq_stats = get_emq_stats(limit=10)

    return templates.TemplateResponse(
        request=request,
        name="pages/admin/dashboard.html",
        context={"visitors": visitors, "emq_stats": emq_stats},
    )


@router.get("/stats")
async def admin_stats(_=Depends(validate_admin_access)):
    """Devuelve JSON con estadísticas para monitoreo externo"""
    get_visitors_query = GetAllVisitorsQuery(list_visitors=legacy.get_all_visitors)
    visitors = await get_visitors_query.execute(limit=1000)
    return {"total_visitors": len(visitors), "status": "active", "database": "connected"}


@router.post("/confirm/{visitor_id}")
async def confirm_sale(
    visitor_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    _=Depends(validate_admin_access),
):
    """
    Confirma una venta y envía evento Purchase a Meta CAPI
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    command = ConfirmSaleCommand(
        get_visitor_by_id=legacy.get_visitor_by_id,
        event_sender=legacy.send_elite_event,
    )
    # The actual execution of the command (which includes sending the Meta event)
    # is now handled by the command itself. We just need to trigger it.
    # The original _bg_send_meta_event logic is now within ConfirmSaleCommand.execute

    # We should add the execution of the command to background tasks
    background_tasks.add_task(
        command.execute,
        visitor_id=visitor_id,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    # Return a synchronous response immediately
    return JSONResponse(
        {
            "status": "success",
            "visitor_id": visitor_id,
            "message": "Evento Purchase encolado correctamente",
        }
    )


@router.get("/signals")
async def audit_signals(_=Depends(validate_admin_access)):
    """
    AUDITORÍA DE SEÑALES (Silicon Valley Signal Quality)
    Compara Leads (DB) vs Eventos Enviados (Flag 'sent_to_meta')
    Muestra la discrepancia real.
    """
    query = GetSignalAuditQuery(get_cursor=legacy.get_cursor)
    result = await query.execute()

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
