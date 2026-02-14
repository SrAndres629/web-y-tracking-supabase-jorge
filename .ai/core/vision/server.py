"""
Neuro-Vision Optic Nerve — MCP Vision Server V2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Production-grade FastAPI server with semantic endpoints,
real WebSocket pub/sub, and code intelligence API.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from .cortex import VisualCortex
    from .event_bus import EventBus
except ImportError:
    from cortex import VisualCortex
    from event_bus import EventBus

# ─────────────────────────────────────────────────────────────────────────────
# Logger
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger("neuro_vision.server")

# ─────────────────────────────────────────────────────────────────────────────
# Application Setup
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Neuro-Vision Optic Nerve V2.0",
    description="Cognitive Visual Cortex — Code Intelligence API",
    version="2.0.0",
)

# Core instances
cortex = VisualCortex()
event_bus = EventBus()

# Wire cortex events → WebSocket broadcast
cortex.subscribe(event_bus.sync_emit)

# Templates path
TEMPLATES_DIR = Path(__file__).parent / "templates"


# ─────────────────────────────────────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    project_root: str


class TelemetryRequest(BaseModel):
    node_id: str
    event_type: str  # execution | error | variable_update | warning
    metadata: dict = {}
    session_id: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# STARTUP EVENT
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    """Set event loop for sync→async bridging."""
    event_bus.set_loop(asyncio.get_running_loop())
    logger.info("🧠 Neuro-Vision V2.0 — Optic Nerve Server started")


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_neuro_map():
    """Serves the 3D interactive neural map visualization."""
    html_path = TEMPLATES_DIR / "neuro_map.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Visualization template not found")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/graph")
async def get_graph():
    """Returns the full code graph in D3-compatible JSON with metrics overlay."""
    try:
        data = cortex.get_graph_json()
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Graph API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def get_health():
    """Returns aggregate project health report."""
    try:
        report = cortex.get_health_report()
        return JSONResponse(content=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# SCAN API
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/scan")
async def trigger_scan(req: ScanRequest):
    """Trigger a full project scan. Returns scan statistics."""
    try:
        await event_bus.emit_scan_started(req.project_root)
        stats = cortex.scan_project(req.project_root)
        return JSONResponse(content=stats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# IMPACT ANALYSIS API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/impact/{node_id:path}")
async def query_impact(node_id: str, depth: int = Query(default=3, ge=1, le=10)):
    """
    Transitive impact analysis: what breaks if this node changes?
    Returns N-depth dependency chain with risk scores.
    """
    try:
        result = cortex.query_impact(node_id, max_depth=depth)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/refs/{symbol_name}")
async def query_references(symbol_name: str):
    """Find all nodes matching a symbol name."""
    try:
        results = cortex.query_references(symbol_name)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CODE QUALITY API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/metrics/{node_id:path}")
async def get_metrics(node_id: str):
    """Get code quality metrics for a specific node."""
    result = cortex.query_metrics(node_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No metrics found for {node_id}")
    return JSONResponse(content=result)


@app.get("/api/smells")
async def get_smells(severity: Optional[str] = Query(default=None)):
    """Get all detected code smells, optionally filtered by severity."""
    try:
        results = cortex.query_smells(severity)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# TEMPORAL MEMORY API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/history")
async def get_scan_history(limit: int = Query(default=10, ge=1, le=100)):
    """Get recent scan history."""
    try:
        results = cortex.query_history(limit)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/search")
async def search_nodes(
    q: str = Query(..., min_length=1, description="Search query"),
    type: Optional[str] = Query(default=None, description="Filter by type: file|class|function"),
):
    """Semantic search across all nodes."""
    try:
        results = cortex.query_search(q, type)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# TELEMETRY API
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/telemetry")
async def ingest_telemetry(req: TelemetryRequest):
    """Ingest a real-time telemetry event from an agent."""
    try:
        event_id = cortex.record_telemetry(
            req.node_id, req.event_type, req.metadata, req.session_id
        )
        await event_bus.emit_telemetry(req.node_id, req.event_type, req.metadata)
        return JSONResponse(content={"status": "ok", "event_id": event_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telemetry")
async def get_telemetry(
    node_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Get recent telemetry events."""
    try:
        results = cortex.query_telemetry(node_id, limit)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# WEBSOCKET — Live Updates
# ─────────────────────────────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint.
    Pushes cortex events (scans, telemetry, node updates) to connected clients.
    Also accepts incoming commands:
      - {"action": "scan", "project_root": "..."}
      - {"action": "telemetry", ...}
    """
    await event_bus.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                action = msg.get("action")

                if action == "scan":
                    project_root = msg.get("project_root", ".")
                    await event_bus.emit_scan_started(project_root)
                    stats = cortex.scan_project(project_root)
                    await websocket.send_json({
                        "type": "scan_result",
                        "data": stats,
                    })

                elif action == "telemetry":
                    cortex.record_telemetry(
                        msg.get("node_id", ""),
                        msg.get("event_type", "execution"),
                        msg.get("metadata", {}),
                        msg.get("session_id"),
                    )

                elif action == "ping":
                    await websocket.send_json({"type": "pong"})

                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": f"Unknown action: {action}"},
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"},
                })

    except WebSocketDisconnect:
        await event_bus.disconnect(websocket)
    except Exception:
        await event_bus.disconnect(websocket)


# ─────────────────────────────────────────────────────────────────────────────
# SERVER LAUNCH
# ─────────────────────────────────────────────────────────────────────────────

def start_server(host: str = "127.0.0.1", port: int = 8888):
    """Launch the Neuro-Vision Optic Nerve server."""
    logger.info(f"🧠 Starting Neuro-Vision V2.0 on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
