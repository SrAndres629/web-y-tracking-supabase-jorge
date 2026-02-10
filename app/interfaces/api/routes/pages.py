"""
🏠 Pages Routes.

Endpoints para páginas HTML.
"""

from __future__ import annotations

import os
import time
import logging
from typing import Optional

from fastapi import APIRouter, Request, Response, BackgroundTasks, Cookie, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.commands.create_visitor import CreateVisitorCommand, CreateVisitorHandler
from app.application.queries.get_content import GetContentQuery, GetContentHandler
from app.interfaces.api.dependencies import (
    get_create_visitor_handler,
    get_get_content_handler,
)
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# System version for cache busting
SYSTEM_VERSION = str(int(time.time()))
templates.env.globals["system_version"] = SYSTEM_VERSION


def _extract_client_info(request: Request) -> dict:
    """Extrae info del cliente."""
    forwarded = request.headers.get("x-forwarded-for")
    cf_ip = request.headers.get("cf-connecting-ip")
    ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "")
    
    return {
        "ip": ip,
        "ua": request.headers.get("user-agent", ""),
        "country": request.headers.get("cf-ipcountry"),
    }


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    background_tasks: BackgroundTasks,
    fbp: Optional[str] = Cookie(default=None, alias="_fbp"),
    fbc: Optional[str] = Cookie(default=None, alias="_fbc"),
    visitor_handler: CreateVisitorHandler = Depends(get_create_visitor_handler),
    content_handler: GetContentHandler = Depends(get_get_content_handler),
):
    """Home page."""
    settings = get_settings()
    client_info = _extract_client_info(request)
    
    # Get fbclid from URL or cookie
    fbclid = request.query_params.get("fbclid")
    if not fbclid and fbc:
        parts = fbc.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
    # Track visitor (background)
    command = CreateVisitorCommand(
        ip_address=client_info["ip"],
        user_agent=client_info["ua"],
        fbclid=fbclid,
        fbp=fbp,
        source="pageview",
        utm_source=request.query_params.get("utm_source"),
        utm_campaign=request.query_params.get("utm_campaign"),
    )
    background_tasks.add_task(visitor_handler.handle, command)
    
    # Get content
    services_query = GetContentQuery(key="services_config")
    contact_query = GetContentQuery(key="contact_config")
    
    services_result = await content_handler.handle(services_query)
    contact_result = await content_handler.handle(contact_query)
    
    services = services_result.unwrap_or([]) if services_result.is_ok else []
    contact = contact_result.unwrap_or({}) if contact_result.is_ok else {}
    
    # Build response
    response = templates.TemplateResponse(
        request=request,
        name="pages/public/home.html",
        context={
            "pixel_id": settings.meta.pixel_id,
            "external_id": "",  # Will be set by JS
            "fbclid": fbclid or "",
            "services": services,
            "contact": contact,
            "google_client_id": settings.external.google_client_id,
            "clarity_id": settings.observability.clarity_project_id,
            "turnstile_site_key": settings.security.turnstile_site_key,
            "flags": {
                "show_testimonials": settings.features.show_testimonials,
                "show_gallery": settings.features.show_gallery,
                "enable_chat_widget": settings.features.enable_chat_widget,
                "cta_variant": settings.features.cta_variant,
                "hero_style": settings.features.hero_style,
            },
        },
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )
    
    # Set cookies
    if not fbp:
        import random
        fbp_val = f"fb.1.{int(time.time()*1000)}.{random.randint(100000000, 999999999)}"
        response.set_cookie(key="_fbp", value=fbp_val, max_age=31536000, httponly=False, secure=True, samesite="lax")
    
    if fbclid:
        fbc_val = f"fb.1.{int(time.time())}.{fbclid}"
        response.set_cookie(key="_fbc", value=fbc_val, max_age=31536000, httponly=False, secure=True, samesite="lax")
    
    return response


@router.head("/")
async def head_root():
    """HEAD response para health checks."""
    return Response(status_code=200)
