"""
🏗️ Architecture Test: No Legacy Paths

Silicon Valley Pattern: Architectural Governance Tests

Este test asegura que no se re-introduzca código legacy en la base de código.
Es un guardián de la arquitectura Clean/DDD.
"""

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON_SCAN_ROOTS = ("app", "api")

# Patrones que NO deben existir en la nueva arquitectura
LEGACY_PATTERNS = {
    "imports": [
        "app.routes",           # Legacy routes (reemplazado por app.interfaces.api.routes)
        "app.templates",        # Templates deben estar en api/templates/
        "app.database",         # Database legacy (reemplazado por app.infrastructure.persistence)
    ],
    "string_literals": [
        "app/templates/",       # Referencias legacy a templates
        "templates/",           # Referencias relativas a templates antiguos
    ]
}

# Archivos que están excluidos de la verificación (tests de auditoría, etc.)
EXCLUDED_FILES = {
    "tests/00_architecture/test_no_legacy_paths.py",  # Este archivo
    "app/domain/__init__.py",  # Narrative text only, no executable imports
}


def _iter_python_files():
    """Itera sobre todos los archivos Python del proyecto"""
    for root_name in PYTHON_SCAN_ROOTS:
        root = PROJECT_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            yield path


def _is_excluded(path: Path) -> bool:
    """Verifica si un archivo está excluido de la auditoría"""
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    return rel in EXCLUDED_FILES


def _legacy_import_violations(tree: ast.AST, rel_path: str):
    """Detecta imports de módulos legacy"""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for legacy in LEGACY_PATTERNS["imports"]:
                if node.module == legacy or node.module.startswith(f"{legacy}."):
                    violations.append(
                        f"{rel_path}:{node.lineno} -> Legacy import: from {node.module}"
                    )
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                for legacy in LEGACY_PATTERNS["imports"]:
                    if mod == legacy or mod.startswith(f"{legacy}."):
                        violations.append(
                            f"{rel_path}:{node.lineno} -> Legacy import: import {mod}"
                        )
    return violations


def _legacy_template_literal_violations(tree: ast.AST, rel_path: str):
    """Detecta strings literales que referencian paths legacy"""
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value.strip()
        for legacy in LEGACY_PATTERNS["string_literals"]:
            if value.startswith(legacy):
                violations.append(
                    f"{rel_path}:{getattr(node, 'lineno', 0)} -> Legacy path: {value}"
                )
    return violations


def test_no_legacy_imports_or_template_paths_in_python():
    """
    Test crítico: Verifica que no existan imports ni referencias a código legacy.
    
    Este test previene:
    - Uso de app.routes (reemplazado por app.interfaces.api.routes)
    - Referencias a templates en app/templates/ (ahora en api/templates/)
    - Imports de app.database legacy (ahora en app.infrastructure.persistence)
    """
    violations = []
    
    for path in _iter_python_files():
        if _is_excluded(path):
            continue
            
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Skip files with syntax errors (keep audit strict for parsable files only)
            continue
            
        violations.extend(_legacy_import_violations(tree, rel_path))
        violations.extend(_legacy_template_literal_violations(tree, rel_path))

    assert not violations, (
        "🚨 Architectural Violation: Legacy imports/template paths detected:\n" 
        + "\n".join(f"  - {v}" for v in violations)
        + "\n\n💡 Refer to ARCHITECTURE.md for correct import patterns."
    )


def test_vercel_includes_api_templates_only():
    """
    Verifica que vercel.json incluya solo templates de api/, no de app/
    """
    vercel_path = PROJECT_ROOT / "vercel.json"
    content = vercel_path.read_text(encoding="utf-8", errors="ignore")
    
    assert "api/templates/**" in content, (
        "vercel.json must include api/templates/** for serverless deployment"
    )
    assert "app/templates/**" not in content, (
        "vercel.json must not include app/templates/** (legacy path removed)"
    )


def test_clean_architecture_imports():
    """
    Verifica que los imports sigan la regla de dependencia de Clean Architecture:
    - Domain no importa de Application ni Infrastructure
    - Application no importa de Infrastructure
    - Interface depende de todas las capas (OK)
    """
    violations = []
    
    domain_path = PROJECT_ROOT / "app" / "domain"
    application_path = PROJECT_ROOT / "app" / "application"
    
    # Verificar que Domain no importe de Application o Infrastructure
    for path in domain_path.rglob("*.py"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        
        # Detectar imports prohibidos en Domain
        prohibited_patterns = [
            "from app.application",
            "from app.infrastructure",
            "import app.application",
            "import app.infrastructure",
        ]
        
        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in prohibited_patterns:
                if pattern in line:
                    violations.append(
                        f"{rel_path}:{line_num} -> Domain layer importing from outer layer: {line.strip()}"
                    )
    
    # Verificar que Application no importe de Infrastructure
    for path in application_path.rglob("*.py"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        
        prohibited_patterns = [
            "from app.infrastructure",
            "import app.infrastructure",
        ]
        
        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in prohibited_patterns:
                if pattern in line:
                    violations.append(
                        f"{rel_path}:{line_num} -> Application layer importing from Infrastructure: {line.strip()}"
                    )
    
    assert not violations, (
        "🚨 Clean Architecture Violation: Dependency Rule violated:\n"
        + "\n".join(f"  - {v}" for v in violations)
        + "\n\n📖 Remember: Dependencies only point INWARD (Domain <- Application <- Infrastructure)"
    )
