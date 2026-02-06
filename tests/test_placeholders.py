import pytest
import os
import re

# 🛡️ PLACEHOLDER AUDITOR CONFIG
# Words that indicate incomplete work
FORBIDDEN_TERMS = [
    "INSERT_KEY", "YOUR_API_KEY", "YOUR_PUBLIC_DSN", 
    "example.com", "Lorem ipsum", "FIXME", "REPLACE_ME", 
    "sk_test_123", "postgres://user:pass"
]

# Files to ignore (e.g., this file itself, tests, logs)
IGNORE_FILES = [
    "test_placeholders.py", 
    ".log", 
    ".pytest_cache", 
    "__pycache__", 
    ".git", 
    "venv", 
    "node_modules",
    "package-lock.json",
    "output.css" # Generated file
]

IGNORE_EXTENSIONS = [".pyc", ".png", ".jpg", ".webp", ".ico", ".svg", ".map"]

# Allow TODOs but warn about them
WARN_TERMS = ["TODO"]

def get_all_files(root_dir):
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_FILES]
        
        for file in files:
            if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            if file in IGNORE_FILES:
                continue
                
            file_list.append(os.path.join(root, file))
    return file_list

def test_no_forbidden_placeholders():
    """
    Scans the entire codebase for forbidden placeholders.
    Fails if any 'INSERT_KEY_HERE' style text is found.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = get_all_files(root_dir)
    
    violations = []
    
    for file_path in files:
        # Skip this test file itself to avoid self-flagging
        if "test_placeholders.py" in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for strictly forbidden pattern
                for term in FORBIDDEN_TERMS:
                    if term in content:
                        # Context extract
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if term in line:
                                violations.append(f"{term} found in {os.path.basename(file_path)}:{i+1}")
        except Exception:
            # Binary files or read errors
            continue
            
    assert not violations, f"❌ PLACEHOLDERS DETECTED:\n" + "\n".join(violations)

def test_warn_todos():
    """
    Warns if there are TODO comments remaining in the code.
    Does not fail the build, but alerts the developer.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = get_all_files(root_dir)
    
    todo_count = 0
    for file_path in files:
        if "test_placeholders.py" in file_path: continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if "TODO" in f.read():
                    todo_count += 1
        except: continue
        
    if todo_count > 0:
        pytest.warns(UserWarning, match=f"⚠️ Found {todo_count} files with TODO comments.")
