"""
NEURO-VISION MCP SERVER v2.0 (WSL OPTIMIZED)
===========================================
High-performance architectural analysis & live telemetry.
Optimized for WSL/Linux environments.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastmcp import FastMCP
from neuro_architect import get_neuro_architect

# --- Advanced Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("neurovision.mcp")

# --- Server Init ---
mcp = FastMCP("Vision Neuronal")

# --- Professional Path Management (God Mode) ---
# PROJECT_ROOT is now just a reference, not a jail.
PROJECT_ROOT = Path("/home/jorand/antigravityobuntu").resolve() 

def validate_path(path_str: str, allow_sensitive: bool = True) -> Path:
    """
    God Mode Path Resolution.
    Allows access to any path in the system if explicitly requested.
    """
    try:
        p = Path(path_str)
        # Verify if it's absolute, otherwise resolve relative to CWD or Project
        if not p.is_absolute():
            target = (Path.cwd() / path_str).resolve()
        else:
            target = p.resolve()

        # LOG WARNING INSTEAD OF BLOCKING
        if not str(target).startswith(str(PROJECT_ROOT)):
            logger.warning(f"⚠️ ACCESSING EXTERNAL PATH: {target}")

        return target
    except Exception as e:
        logger.error(f"Path Error: {e}")
        raise

from neuro_architect import get_cortex

# --- Core Tools (Mathematical Integrity) ---

@mcp.tool()
async def list_files(directory: str = ".", recursive: bool = False) -> dict:
    """List system files with architectural metadata (God Mode)."""
    try:
        root = validate_path(directory)
        files = []
        pattern = "**/*" if recursive else "*"
        
        for p in root.glob(pattern):
            # Reduced noise filter for God Mode
            if any(part in SENSITIVE_DIRS for part in p.parts):
                 continue
            
            is_dir = p.is_dir()
            files.append({
                "name": p.name,
                "path": str(p), # Absolute path for God Mode
                "type": "directory" if is_dir else "file",
                "size": p.stat().st_size if not is_dir else 0,
                "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
            })
            if len(files) >= 1000: break 
                
        return {"success": True, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def read_file(path: str) -> dict:
    """Read file content (God Mode - No Restrictions)."""
    try:
        target = validate_path(path)
        if not target.is_file():
            return {"success": False, "error": "Not a file"}
        return {"success": True, "content": target.read_text(encoding="utf-8")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def write_file(path: str, content: str) -> dict:
    """Write files anywhere (God Mode)."""
    try:
        target = validate_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(target)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def refresh_vision(target_project: str = ".") -> dict:
    """Deep Cortical Scan: Builds the holographic memory."""
    try:
        root = validate_path(target_project)
        cortex = get_cortex(str(root))
        cortex.refresh_scan()
        return {"success": True, "message": "Cortex synced with reality."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def consult_memory(query: str, target_project: str = ".") -> dict:
    """
    Infinite Context Recall.
    Asks the Cortex for relevant code, concepts, or memories based on semantic relevance.
    """
    try:
        root = validate_path(target_project)
        cortex = get_cortex(str(root))
        memories = cortex.recall(query)
        return {"success": True, "memories": memories}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def visualize_cortex(target_project: str = ".") -> dict:
    """Generates the advanced 3D Holographic Map of the project brain."""
    try:
        root = validate_path(target_project)
        cortex = get_cortex(str(root))
        json_path = cortex.export_holographic_map()
        return {"success": True, "data_path": str(json_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def send_telemetry(node: str, event_type: str, metadata: dict = None, project: str = ".") -> dict:
    """Injects 'feelings' (execution/error events) into the Cortex."""
    try:
        root = validate_path(project)
        cortex = get_cortex(str(root))
        cortex.ingest_telemetry(node, event_type, metadata or {})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    logger.info(f"Cortex Online: Jail set to {PROJECT_ROOT}")
    mcp.run()
