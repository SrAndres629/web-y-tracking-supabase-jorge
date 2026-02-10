"""
📊 Tracking Routes.

Endpoints para tracking de eventos.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from app.application.commands.track_event import TrackEventCommand, TrackEventHandler
from app.application.dto.tracking_dto import TrackEventRequest, TrackingContext
from app.interfaces.api.dependencies import get_track_event_handler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/track", tags=["tracking"])


def _extract_tracking_context(request: Request) -> TrackingContext:
    """Extrae contexto técnico del request."""
    # Headers de Cloudflare
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown")
    
    return TrackingContext(
        ip_address=ip,
        user_agent=request.headers.get("user-agent", ""),
        country=request.headers.get("cf-ipcountry"),
        city=request.headers.get("cf-ipcity"),
        region=request.headers.get("cf-region") or request.headers.get("cf-region-code"),
    )


@router.post("/event")
async def track_event(
    request: Request,
    data: TrackEventRequest,
    background_tasks: BackgroundTasks,
    handler: TrackEventHandler = Depends(get_track_event_handler),
):
    """
    Track an event.
    
    Deduplicación automática, persistencia y envío a trackers externos.
    """
    context = _extract_tracking_context(request)
    command = TrackEventCommand(request=data, context=context)
    
    # Ejecutar handler
    result = await handler.handle(command)
    
    return JSONResponse(
        content={
            "success": result.success,
            "event_id": result.event_id,
            "status": result.status,
            "message": result.message,
        },
        headers={"Cache-Control": "no-store"},
    )


@router.get("/health")
async def tracking_health():
    """Health check del sistema de tracking."""
    return {"status": "ok", "service": "tracking"}
