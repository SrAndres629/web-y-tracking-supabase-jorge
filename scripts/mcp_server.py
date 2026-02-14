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

# --- Professional Path Management (WSL Optimized) ---
PROJECT_ROOT = Path("/home/jorand/antigravityobuntu").resolve()
SENSITIVE_DIRS = {".git", ".env", ".ssh", "__pycache__", "node_modules", ".venv", "venv", "dist"}

def validate_path(path_str: str, allow_sensitive: bool = False) -> Path:
    """
    Normalizes and validates paths within the WSL project jail.
    Handles both absolute and relative inputs.
    """
    try:
        # Resolve path
        p = Path(path_str)
        if not p.is_absolute():
            # If relative, assume relative to project root for consistency
            target = (PROJECT_ROOT / path_str).resolve()
        else:
            target = p.resolve()

        # Jail check
        if not str(target).startswith(str(PROJECT_ROOT)):
            # If it's a Windows-style path being passed from an agent (rare but possible)
            if "mnt/c" in str(target):
                 # Try to map it back if it's the project dir
                 if "antigravityobuntu" in str(target).lower():
                     # This is a bit hacky but helps with cross-env agents
                     target = PROJECT_ROOT
            
            if not str(target).startswith(str(PROJECT_ROOT)):
                raise PermissionError(f"NeuroVision Jail Breach Attempt: {target} is outside {PROJECT_ROOT}")

        # Sensitivity check
        if not allow_sensitive:
            for part in target.parts:
                if part in SENSITIVE_DIRS:
                    raise PermissionError(f"Access Denied: Restricted component '{part}' in path.")

        return target
    except Exception as e:
        logger.error(f"Path Validation Error: {e}")
        raise

# --- Core Tools (Mathematical Integrity) ---

@mcp.tool()
async def list_files(directory: str = ".", recursive: bool = False) -> dict:
    """List system files with architectural metadata."""
    try:
        root = validate_path(directory)
        files = []
        pattern = "**/*" if recursive else "*"
        
        for p in root.glob(pattern):
            # Skip hidden and sensitive
            if any(part.startswith('.') or part in SENSITIVE_DIRS for part in p.parts):
                continue
            
            is_dir = p.is_dir()
            files.append({
                "name": p.name,
                "path": str(p.relative_to(PROJECT_ROOT)),
                "type": "directory" if is_dir else "file",
                "size": p.stat().st_size if not is_dir else 0,
                "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
            })
            if len(files) >= 500: break # Safety cap
                
        return {"success": True, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def read_file(path: str) -> dict:
    """Read file content with UTF-8 normalization."""
    try:
        target = validate_path(path)
        if not target.is_file():
            return {"success": False, "error": "Not a file"}
        return {"success": True, "content": target.read_text(encoding="utf-8")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def write_file(path: str, content: str) -> dict:
    """Safely write files into the project structure."""
    try:
        target = validate_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(target.relative_to(PROJECT_ROOT))}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def refresh_vision(target_project: str = ".") -> dict:
    """Forces a deep architectural re-scan using the static analysis engine."""
    try:
        root = validate_path(target_project)
        architect = get_neuro_architect(str(root))
        architect.refresh() # Trigger re-scan
        return {"success": True, "message": f"Graph rebuilt for {root.name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def analyze_impact(target_node: str, target_project: str = ".") -> dict:
    """Mathematical prediction of ripple effects for code changes."""
    try:
        root = validate_path(target_project)
        neuro = get_neuro_architect(str(root))
        prediction = neuro.analyze_impact(target_node)
        return {"success": True, "prediction": prediction.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def visualize_architecture(action: str = "render", target_project: str = ".") -> dict:
    """Generates a dynamic 3D graph of the system architecture."""
    try:
        root = validate_path(target_project)
        neuro = get_neuro_architect(str(root))
        if action == "render":
            html_path = neuro.export_neuro_map()
            return {"success": True, "html_path": str(html_path)}
        return {"success": True, "data": neuro.get_brain_state()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def send_telemetry(node: str, event_type: str, metadata: dict = None, project: str = ".") -> dict:
    """Ingests real-time events to heat-map the architectural graph."""
    try:
        root = validate_path(project)
        neuro = get_neuro_architect(str(root))
        neuro.ingest_telemetry(node, event_type, metadata or {})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    logger.info(f"Cortex Online: Jail set to {PROJECT_ROOT}")
    mcp.run()
