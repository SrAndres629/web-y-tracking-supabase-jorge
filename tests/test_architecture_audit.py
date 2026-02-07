import os
import re
import ast
import pytest
from pathlib import Path

# =================================================================
# 🛡️ THE ARCHITECTURE POLICE (Senior Google Standard)
# =================================================================
# This suite mathematically enforces hygiene, security, and quality.
# Any failure here BLOCKS deployment in git_sync.py.
# =================================================================

BASE_DIR = Path(__file__).parent.parent
FORBIDDEN_TERMS = [
    "REQUIRED_IN_VERCEL", "TODO", "FIXME", "REEMPLAZAR_AQUI", 
    "example.com", "placeholder", "YOUR_API_KEY", "sk_test",
    "REPLACE_ME", "INSERT_KEY"
]

# Files/Dirs to ignore
IGNORE_DIRS = {".git", "__pycache__", "venv", "node_modules", ".pytest_cache", ".hypothesis", ".vercel", ".cursor", "scripts"}
IGNORE_FILES = {
    "test_architecture_audit.py", "git_sync.py", "AI_CONTEXT.md", 
    "README.md", "ENGINEERING_LOG.md", "requirements.txt"
}
IGNORE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".map", ".json", ".log"}

def get_target_files():
    """Recursively yields all relevant source files"""
    for root, dirs, files in os.walk(str(BASE_DIR)):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file in IGNORE_FILES: continue
            if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS): continue
            yield Path(root) / file

# --- AUDITORS ---

def audit_placeholders(path, content):
    """Fails if forbidden placeholders or TODOs are found"""
    violations = []
    for term in FORBIDDEN_TERMS:
        if term in content:
            # Simple line finding
            for i, line in enumerate(content.splitlines()):
                if term in line:
                    violations.append(f"L{i+1}: Found prohibited term '{term}'")
    return violations

def audit_hardcoded_secrets(path, content):
    """Fails on likely hardcoded keys (Entropy/Pattern heuristics)"""
    violations = []
    # Patterns for common secret formats
    secret_patterns = [
        r'sk_live_[a-zA-Z0-9]{20,}',  # Stripe-like
        r'AIza[0-9A-Za-z-_]{35}',     # Google API Keys
        r'xox[baprs]-[0-9a-zA-Z-]{10,}', # Slack
        r'ghp_[a-zA-Z0-9]{36}',       # GitHub
        # High entropy strings in assignments (e.g. key = "abc123xyz...")
        r'=\s*["\'](?=[a-zA-Z0-9]*[A-Z])(?=[a-zA-Z0-9]*[a-z])(?=[a-zA-Z0-9]*[0-9])[a-zA-Z0-9]{32,}["\']'
    ]
    
    for pattern in secret_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_no = content.count('\n', 0, match.start()) + 1
            violations.append(f"L{line_no}: Likely hardcoded secret detected (Pattern: {pattern[:15]}...)")
    
    return violations

def audit_python_hygiene(path):
    """AST-based audit for Python files (prints, function length)"""
    if path.suffix != '.py':
        return []

    violations = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return [f"ERROR: Could not parse AST: {e}"]

    for node in ast.walk(tree):
        # 1. Print Detection (Hygiene)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
            violations.append(f"L{node.lineno}: Prohibited 'print()' found in production code. Use 'logger' instead.")

        # 2. Function Length Audit (Technical Debt)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for noqa suppression in the function definition lines
            with open(path, "r", encoding="utf-8") as f:
                content_lines = f.readlines()
                # Check from lineno to the first few lines of the function
                found_noqa = False
                for i in range(node.lineno - 1, min(node.lineno + 5, len(content_lines))):
                    if "# noqa" in content_lines[i]:
                        found_noqa = True
                        break
                if found_noqa:
                    continue

            length = node.end_lineno - node.lineno
            if length > 50:
                violations.append(f"L{node.lineno}: Function '{node.name}' is too long ({length} lines). Threshold is 50. Refactor requested.")

    return violations

# --- PYTEST RUNNER ---

@pytest.mark.parametrize("file_path", list(get_target_files()))
def test_architecture_violations(file_path):
    """Master validation gate for all files"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    errors = []
    
    # Run generic auditors
    errors.extend(audit_placeholders(file_path, content))
    errors.extend(audit_hardcoded_secrets(file_path, content))
    
    # Run language-specific auditors
    if file_path.suffix == '.py':
        errors.extend(audit_python_hygiene(file_path))

    if errors:
        msg = f"\n🚨 ARCHITECTURE VIOLATIONS in [{file_path.relative_to(BASE_DIR)}]:\n"
        msg += "\n".join(errors)
        pytest.fail(msg)

def test_system_coherence():
    """Checks for overall project structural integrity"""
    # 1. Verify existence of critical paths
    critical_paths = ["app/config.py", "git_sync.py", "AI_CONTEXT.md", "ENGINEERING_LOG.md"]
    for cp in critical_paths:
        assert (BASE_DIR / cp).exists(), f"CRITICAL: System file missing: {cp}"
