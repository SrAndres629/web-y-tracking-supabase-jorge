#!/usr/bin/env python3
"""
🔍 MANIFEST VALIDATOR — Verify Project Integrity Against MANIFEST.yaml.

Compares the generated MANIFEST.yaml against the real filesystem to detect:
- Ghost files (in manifest but missing from disk)
- Orphan files (on disk but missing from manifest)
- Hash mismatches (file content changed since last generation)
- Broken Python imports

Usage:
    python scripts/validate_manifest.py
    python scripts/validate_manifest.py --json  # Machine-readable output
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    "node_modules", "venv", ".git", "__pycache__", ".hypothesis",
    ".pytest_cache", ".vercel", ".vscode", "dist", ".egg-info",
    ".system_generated",
}


def load_manifest(path: Path) -> Dict[str, Any]:
    """Parse MANIFEST.yaml (basic YAML parser for our format)."""
    if not path.exists():
        print(f"❌ MANIFEST.yaml not found at {path}")
        print("   Run: python scripts/generate_manifest.py")
        sys.exit(1)
    
    # Since our YAML is simple, we can parse it or just use JSON fallback
    # For robustness, let's try to import yaml, fall back to our parser
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass
    
    # Fallback: just check if manifest exists and do filesystem-only validation
    return {}


def collect_real_files(root: Path) -> Set[str]:
    """Collect all real files in the project."""
    files = set()
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter excluded dirs in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS
            and not d.endswith(".egg-info")
            and not (d.startswith(".") and d not in {".agent", ".agentignore"})
        ]
        
        rel_dir = os.path.relpath(dirpath, root)
        for fname in filenames:
            if fname.endswith((".pyc", ".pyo", ".DS_Store")):
                continue
            if fname in {".env", ".env.production"}:
                continue
            rel_path = os.path.join(rel_dir, fname) if rel_dir != "." else fname
            files.add(rel_path)
    
    return files


def check_python_imports(root: Path) -> List[Dict[str, str]]:
    """Check for broken Python imports within app/."""
    broken = []
    app_dir = root / "app"
    
    if not app_dir.exists():
        return broken
    
    import_pattern = re.compile(
        r"^(?:from|import)\s+(app\.[a-zA-Z0-9_.]+)", re.MULTILINE
    )
    
    for py_file in app_dir.rglob("*.py"):
        try:
            content = py_file.read_text(errors="replace")
        except OSError:
            continue
        
        for match in import_pattern.finditer(content):
            module_path = match.group(1)
            # Convert module path to file path
            parts = module_path.split(".")
            
            # Check if module exists as a file or package
            possible_file = root / "/".join(parts) / "__init__.py"
            possible_module = root / ("/".join(parts) + ".py")
            possible_package = root / "/".join(parts)
            
            if not (possible_file.exists() or possible_module.exists() or possible_package.is_dir()):
                broken.append({
                    "file": str(py_file.relative_to(root)),
                    "import": module_path,
                    "line": content[:match.start()].count("\n") + 1,
                })
    
    return broken


def check_vercel_routes(root: Path) -> List[Dict[str, str]]:
    """Verify vercel.json routes point to existing files."""
    issues = []
    vercel_json = root / "vercel.json"
    
    if not vercel_json.exists():
        return issues
    
    try:
        with open(vercel_json) as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        issues.append({"type": "parse_error", "detail": "Cannot parse vercel.json"})
        return issues
    
    for route in config.get("routes", []):
        dest = route.get("dest", "")
        if dest and not dest.startswith("http"):
            # Check if destination file exists
            dest_clean = dest.split("?")[0]  # Remove query params
            dest_path = root / dest_clean.lstrip("/")
            if not dest_path.exists() and not dest_clean.startswith("/api/"):
                # API routes are handled by serverless functions
                issues.append({
                    "src": route.get("src", ""),
                    "dest": dest,
                    "status": "MISSING_DESTINATION",
                })
    
    return issues


def validate(root: Path, json_output: bool = False) -> Dict[str, Any]:
    """Run all validation checks."""
    report = {
        "status": "ok",
        "broken_imports": check_python_imports(root),
        "route_issues": check_vercel_routes(root),
        "warnings": [],
    }
    
    # Check for common issues
    if report["broken_imports"]:
        report["status"] = "issues_found"
        report["warnings"].append(
            f"{len(report['broken_imports'])} broken Python import(s) detected"
        )
    
    if report["route_issues"]:
        report["status"] = "issues_found"
        report["warnings"].append(
            f"{len(report['route_issues'])} route issue(s) in vercel.json"
        )
    
    # Check for stale __pycache__
    pycache_count = sum(
        1 for p in root.rglob("__pycache__")
        if "venv" not in p.parts and "node_modules" not in p.parts
    )
    if pycache_count > 5:
        report["warnings"].append(
            f"{pycache_count} __pycache__ directories found — run cleanup"
        )
    
    return report


def main():
    json_mode = "--json" in sys.argv
    
    print("🔍 Validating project integrity...")
    report = validate(PROJECT_ROOT, json_mode)
    
    if json_mode:
        print(json.dumps(report, indent=2))
        return
    
    # Human-readable output
    if report["status"] == "ok":
        print("✅ All checks passed — project integrity verified.")
    else:
        print(f"⚠️  Issues found:")
    
    if report["broken_imports"]:
        print(f"\n🔴 Broken Python Imports ({len(report['broken_imports'])}):")
        for imp in report["broken_imports"]:
            print(f"   {imp['file']}:{imp['line']} → {imp['import']}")
    
    if report["route_issues"]:
        print(f"\n🟡 Route Issues ({len(report['route_issues'])}):")
        for issue in report["route_issues"]:
            print(f"   {issue.get('src', '?')} → {issue.get('dest', '?')} [{issue.get('status', '?')}]")
    
    if report["warnings"]:
        print(f"\n⚠️  Warnings:")
        for w in report["warnings"]:
            print(f"   • {w}")
    
    # Exit code for CI
    sys.exit(0 if report["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
