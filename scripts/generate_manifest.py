#!/usr/bin/env python3
"""
🏗️ MANIFEST GENERATOR — Single Source of Truth for Project Structure.

Generates MANIFEST.yaml with the complete directory tree, file hashes,
API routes, and metadata. Designed for AI agent consumption.

Usage:
    python scripts/generate_manifest.py
    python scripts/generate_manifest.py --output MANIFEST.yaml
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project root is parent of scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    "node_modules", "venv", ".git", "__pycache__", ".hypothesis",
    ".pytest_cache", ".vercel", ".vscode", "dist", ".egg-info",
    ".system_generated",
}

# File patterns to exclude
EXCLUDE_PATTERNS = {".pyc", ".pyo", ".DS_Store", ".env", ".env.production"}


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]  # Short hash for readability
    except (OSError, PermissionError):
        return "ERROR"


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded."""
    parts = path.parts
    for part in parts:
        if part in EXCLUDE_DIRS or part.endswith(".egg-info"):
            return True
        if part.startswith(".") and part not in {".agent", ".agentignore", ".gitignore",
                                                   ".gitlab-ci.yml", ".djlintrc",
                                                   ".dockerignore", ".eslintrc.json",
                                                   ".prettierrc", ".stylelintrc.json",
                                                   ".stylelintignore", ".coveragerc"}:
            # Skip hidden dirs except known config
            if os.path.isdir(path):
                return True
    return False


def scan_directory(root: Path, base: Path) -> Dict[str, Any]:
    """Recursively scan a directory and build a tree structure."""
    tree: Dict[str, Any] = {"_type": "directory", "_children": {}}
    
    try:
        entries = sorted(root.iterdir())
    except PermissionError:
        return tree
    
    for entry in entries:
        rel = entry.relative_to(base)
        
        if should_exclude(rel):
            continue
        
        name = entry.name
        if name in EXCLUDE_PATTERNS or any(name.endswith(p) for p in EXCLUDE_PATTERNS):
            continue
        
        if entry.is_dir():
            subtree = scan_directory(entry, base)
            child_count = _count_files(subtree)
            if child_count > 0:  # Only include non-empty dirs
                subtree["_files"] = child_count
                tree["_children"][name] = subtree
        elif entry.is_file():
            size = entry.stat().st_size
            tree["_children"][name] = {
                "_type": "file",
                "_size": size,
                "_hash": sha256_file(entry),
            }
    
    return tree


def _count_files(tree: Dict[str, Any]) -> int:
    """Count total files in a tree."""
    count = 0
    for v in tree.get("_children", {}).values():
        if v.get("_type") == "file":
            count += 1
        elif v.get("_type") == "directory":
            count += _count_files(v)
    return count


def extract_api_routes(root: Path) -> List[Dict[str, str]]:
    """Extract API routes from vercel.json (supports routes, rewrites, builds)."""
    routes = []
    vercel_json = root / "vercel.json"
    if vercel_json.exists():
        try:
            with open(vercel_json) as f:
                config = json.load(f)
            # Parse routes
            for route in config.get("routes", []):
                routes.append({"source": route.get("src", ""), "destination": route.get("dest", ""), "type": "route"})
            # Parse rewrites
            for rewrite in config.get("rewrites", []):
                routes.append({"source": rewrite.get("source", ""), "destination": rewrite.get("destination", ""), "type": "rewrite"})
            # Parse builds
            for build in config.get("builds", []):
                routes.append({"source": build.get("src", ""), "destination": build.get("use", ""), "type": "build"})
        except (json.JSONDecodeError, OSError):
            pass
    return routes


def extract_fastapi_routers(root: Path) -> List[Dict[str, str]]:
    """Extract FastAPI router prefixes from route files."""
    routers = []
    routes_dir = root / "app" / "interfaces" / "api" / "routes"
    if routes_dir.exists():
        for py_file in sorted(routes_dir.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
            try:
                content = py_file.read_text(errors="replace")
                for line in content.splitlines():
                    if "APIRouter" in line and "prefix" in line:
                        # Extract prefix value
                        start = line.find('prefix="') or line.find("prefix='")
                        if start >= 0:
                            start += len('prefix="')
                            end = line.find('"', start) if '"' in line[start:] else line.find("'", start)
                            if end > start:
                                prefix = line[start:end]
                                routers.append({
                                    "file": py_file.name,
                                    "prefix": prefix,
                                })
            except OSError:
                pass
    return routers


def generate_manifest(root: Path) -> Dict[str, Any]:
    """Generate the complete manifest."""
    tree = scan_directory(root, root)
    
    manifest = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "stats": {
            "total_files": _count_files(tree),
            "total_dirs": sum(
                1 for v in tree.get("_children", {}).values()
                if v.get("_type") == "directory"
            ),
        },
        "routes": {
            "vercel": extract_api_routes(root),
            "fastapi": extract_fastapi_routers(root),
        },
        "tree": tree["_children"],
    }
    
    return manifest


def dict_to_yaml(d: Any, indent: int = 0) -> str:
    """Minimal YAML serializer (no PyYAML dependency)."""
    lines: List[str] = []
    prefix = "  " * indent
    
    if isinstance(d, dict):
        for key, value in d.items():
            formatted_key = _yaml_value(key)
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{formatted_key}:")
                lines.append(dict_to_yaml(value, indent + 1))
            else:
                lines.append(f"{prefix}{formatted_key}: {_yaml_value(value)}")
    elif isinstance(d, list):
        for item in d:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                lines.append(dict_to_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {_yaml_value(item)}")
    
    return "\n".join(lines)


def _yaml_value(v: Any) -> str:
    """Format a scalar value for YAML."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in ":#{}[]|>&*!%@`"):
        return f'"{s}"'
    return s


def main():
    output_path = PROJECT_ROOT / "MANIFEST.yaml"
    
    # Allow custom output path
    if len(sys.argv) > 2 and sys.argv[1] == "--output":
        output_path = Path(sys.argv[2])
    
    print(f"🏗️  Scanning project: {PROJECT_ROOT}")
    manifest = generate_manifest(PROJECT_ROOT)
    
    yaml_content = f"# MANIFEST.yaml — Single Source of Truth\n"
    yaml_content += f"# Generated: {manifest['generated_at']}\n"
    yaml_content += f"# DO NOT EDIT MANUALLY — Run: python scripts/generate_manifest.py\n\n"
    yaml_content += dict_to_yaml(manifest)
    
    output_path.write_text(yaml_content)
    
    print(f"✅ Manifest generated: {output_path}")
    print(f"   📁 {manifest['stats']['total_files']} files in {manifest['stats']['total_dirs']} top-level dirs")
    print(f"   🛤️  {len(manifest['routes']['vercel'])} Vercel routes, {len(manifest['routes']['fastapi'])} FastAPI routers")


if __name__ == "__main__":
    main()
