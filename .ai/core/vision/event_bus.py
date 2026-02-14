"""
Event Bus — MCP Vision Neuronal V2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Async event bus for real-time WebSocket pub/sub.
Broadcasts cortex events to all connected visualization clients.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger("visual_cortex.event_bus")


@dataclass
class EventBus:
    """
    Singleton async event bus that bridges the synchronous Cortex
    with async WebSocket connections.

    Usage:
        bus = EventBus()
        cortex.subscribe(bus.sync_emit)  # Cortex pushes events here
        # In WebSocket handler:
        await bus.connect(websocket)
    """
    _connections: Set[WebSocket] = field(default_factory=set)
    _event_queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=1000))
    _loop: Optional[asyncio.AbstractEventLoop] = field(default=None)

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop reference for sync→async bridging."""
        self._loop = loop

    # ── Connection Management ────────────────────────────────────────────

    async def connect(self, ws: WebSocket):
        """Register a new WebSocket client."""
        await ws.accept()
        self._connections.add(ws)
        logger.info(f"🔌 WebSocket connected. Total clients: {len(self._connections)}")

        # Send initial state
        await ws.send_json({
            "type": "connected",
            "data": {"clients": len(self._connections)},
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def disconnect(self, ws: WebSocket):
        """Remove a WebSocket client."""
        self._connections.discard(ws)
        logger.info(f"🔌 WebSocket disconnected. Total clients: {len(self._connections)}")

    # ── Event Broadcasting ───────────────────────────────────────────────

    async def broadcast(self, event: Dict[str, Any]):
        """Broadcast an event to all connected WebSocket clients."""
        if not self._connections:
            return

        message = json.dumps(event, default=str)
        dead_connections: List[WebSocket] = []

        for ws in self._connections.copy():
            try:
                await ws.send_text(message)
            except Exception:
                dead_connections.append(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self._connections.discard(ws)

    def sync_emit(self, event: Dict[str, Any]):
        """
        Synchronous callback for the Cortex event system.
        Thread-safely queues events for async broadcasting.
        """
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast(event), self._loop
            )

    # ── Convenience Methods ──────────────────────────────────────────────

    async def emit_scan_started(self, project_root: str):
        """Emit a scan_started event."""
        await self.broadcast({
            "type": "scan_started",
            "data": {"project_root": project_root},
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def emit_scan_completed(self, stats: Dict):
        """Emit a scan_completed event."""
        await self.broadcast({
            "type": "scan_completed",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def emit_telemetry(self, node_id: str, event_type: str, metadata: Dict):
        """Emit a telemetry event."""
        await self.broadcast({
            "type": "telemetry_received",
            "data": {
                "node_id": node_id,
                "event_type": event_type,
                "metadata": metadata,
            },
            "timestamp": datetime.utcnow().isoformat(),
        })

    @property
    def client_count(self) -> int:
        """Number of connected clients."""
        return len(self._connections)
