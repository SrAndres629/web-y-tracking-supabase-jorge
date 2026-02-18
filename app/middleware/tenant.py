"""Tenant enforcement middleware for multi-tenant tracking."""

from __future__ import annotations

from starlette.datastructures import State
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import settings


class TenantMiddleware:
    """Ensures the tenant header is resolved and stored on the request."""

    HEADER_NAME = "x-tenant-id"

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        tenant_candidate = headers.get(self.HEADER_NAME)
        resolved = settings.resolve_tenant(tenant_candidate)

        if not settings.is_tenant_allowed(resolved):
            response = JSONResponse(
                status_code=403,
                content={"detail": "Tenant no permitido"},
            )
            await response(scope, receive, send)
            return

        state: State = scope.setdefault("state", State())
        state.tenant_id = resolved

        await self.app(scope, receive, send)
