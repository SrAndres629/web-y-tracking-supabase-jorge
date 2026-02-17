
import os
import ast
import sys
import logging
from pathlib import Path
from typing import Set, Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("CortexAudit")

PROJECT_ROOT = Path("/home/jorand/antigravityobuntu")
APP_DIR = PROJECT_ROOT / "app"
TEMPLATES_DIR = PROJECT_ROOT / "api/templates"

def get_all_python_files(directory: Path) -> List[Path]:
    return list(directory.rglob("*.py"))

def get_all_template_files(directory: Path) -> Set[str]:
    files = set()
    for f in directory.rglob("*.html"):
        relative = f.relative_to(directory)
        files.add(str(relative))
    return files

def extract_template_references(py_file: Path) -> Set[str]:
    """Finds string literals that look like template paths in a python file."""
    try:
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        logger.warning(f"Failed to parse {py_file}: {e}")
        return set()

    refs = set()
    for node in ast.walk(tree):
        # Look for calls to templates.TemplateResponse("name.html", ...)
        if isinstance(node, ast.Call):
            # Check if it's TemplateResponse
            is_template_response = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == "TemplateResponse":
                is_template_response = True
            
            if is_template_response and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    refs.add(arg0.value)
            elif is_template_response and node.keywords:
                 for keyword in node.keywords:
                     if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                         refs.add(keyword.value.value)

        # Also just generic string search (fallback)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if val.endswith(".html") and "/" in val:
                refs.add(val)
    return refs

def audit_templates():
    logger.info("🔍 AUDIT: Analyzing Template Usage...")
    
    all_templates = get_all_template_files(TEMPLATES_DIR)
    logger.info(f"Found {len(all_templates)} total template files.")

    referenced_templates = set()
    py_files = get_all_python_files(APP_DIR)
    
    # Also check specific strategic files
    py_files.append(PROJECT_ROOT / "main.py")

    for py_file in py_files:
        refs = extract_template_references(py_file)
        referenced_templates.update(refs)

    # Cross-reference
    missing = []     # Templates referenced in code but missing on disk
    orphaned = []    # Templates on disk but never referenced in code/templates

    # 1. Check Python References
    for ref in referenced_templates:
        found_ref = False
        for tmpl in all_templates:
             if tmpl.endswith(ref):
                 found_ref = True
                 break
        if not found_ref:
            missing.append(f"[Python] {ref}")

    # 2. Check Template-to-Template Includes (Recursive)
    # Build a set of ALL referenced templates (starting from python refs)
    all_referenced = set()
    
    def resolve_template(ref_name):
        # Tries to find the actual file path for a reference
        for t in all_templates:
             if t.endswith(ref_name):
                 return t
        return None

    # Queue for BFS
    queue = []
    for ref in referenced_templates:
        resolved = resolve_template(ref)
        if resolved and resolved not in all_referenced:
             all_referenced.add(resolved)
             queue.append(resolved)

    checked_templates = set()
    
    while queue:
        current_tmpl = queue.pop(0)
        if current_tmpl in checked_templates:
            continue
        checked_templates.add(current_tmpl)
        
        # Parse this template for {% include "..." %} or {% extends "..." %}
        try:
            with open(TEMPLATES_DIR / current_tmpl, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Regex for includes/extends
            import re
            # Matches {% include "foo.html" %} or {% extends 'bar.html' %}
            # Captures the filename in group 2
            matches = re.finditer(r'{%\s*(include|extends)\s+[\'"]([^\'"]+)[\'"]', content)
            
            for m in matches:
                ref = m.group(2)
                resolved = resolve_template(ref)
                if resolved:
                    if resolved not in all_referenced:
                        all_referenced.add(resolved)
                        queue.append(resolved)
                else:
                    if not ref.startswith("components/"): # Ignore dynamic components for now
                        missing.append(f"[{current_tmpl}] {ref}")
                        
        except Exception as e:
            logger.warning(f"Failed to parse template {current_tmpl}: {e}")

    # 3. Detect Orphans
    for tmpl in all_templates:
        if tmpl not in all_referenced:
             # Exclude base layouts which might be implicitly used or base
             if not (tmpl.startswith("layouts/") or tmpl.startswith("components/")):
                 orphaned.append(tmpl)

    if missing:
        logger.error(f"❌ BROKEN ROUTES / INCLUDES:")
        for m in missing:
            logger.error(f"   - {m}")
    else:
        logger.info("✅ All referenced templates exist.")

    if orphaned:
        logger.warning(f"⚠️ ORPHANED TEMPLATES (Not reachable from Python routes):")
        for o in orphaned:
            logger.warning(f"   - {o}")
    else:
        logger.info("✅ No orphaned page templates found.")
    
    return len(missing) == 0

def audit_config():
    logger.info("\n🔍 AUDIT: Analyzing Configuration Logic...")
    try:
        sys.path.append(str(PROJECT_ROOT))
        from app.config import settings
        
        issues = []
        if settings.META_PIXEL_ID and not settings.META_API_VERSION:
            issues.append("META_PIXEL_ID is set but META_API_VERSION is missing (defaulting? validation needed).")
        
        if settings.META_ACCESS_TOKEN and not settings.META_PIXEL_ID:
            issues.append("Access Token present but Pixel ID missing.")

        if not issues:
             logger.info("✅ Configuration looks logical.")
        else:
             for i in issues:
                 logger.error(f"❌ CONFIG ISSUE: {i}")
             return False
    except Exception as e:
        logger.error(f"❌ CRITICAL: Could not import app.config: {e}")
        return False
    return True

if __name__ == "__main__":
    logger.info("🚀 STARTING CORTEX SYSTEM AUDIT")
    if audit_templates() and audit_config():
        logger.info("\n✅ SYSTEM AUDIT PASSED. ARCHITECTURE IS SOUND.")
        sys.exit(0)
    else:
        logger.error("\n❌ SYSTEM AUDIT FAILED. CRITICAL ISSUES FOUND.")
        sys.exit(1)
