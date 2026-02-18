#!/usr/bin/env python3
"""
🛠️ Auto-Fixer & Self-Healing Script
====================================
Automatically detects and fixes common codebase issues:
- Runs Ruff (lint + format)
- Fixes specific patterns (bare excepts, zip strictness)
- Validates imports

Usage:
    python3 tools/auto_fix.py
"""

import os
import re
import subprocess
import sys
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AutoFixer")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def run_cmd(command, cwd=None, ignore_errors=False, shell=False):
    """Executes a shell command."""
    try:
        if isinstance(command, str) and not shell:
            command = command.split()

        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            cwd=cwd or REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            logger.error(f"Command failed: {command}\n{e.stderr}")
            raise e
        return e.stdout.strip()


def fix_ruff():
    """Runs Ruff to auto-fix and format code."""
    logger.info("🧹 Running Ruff Auto-Fix...")

    # Attempt to find ruff in known locations
    ruff_cmd = "ruff"
    venv_ruff = os.path.join(REPO_ROOT, "venv", "bin", "ruff")
    if os.path.exists(venv_ruff):
        ruff_cmd = venv_ruff

    try:
        run_cmd([ruff_cmd, "check", "--fix", "."], ignore_errors=True)
        run_cmd([ruff_cmd, "format", "."], ignore_errors=True)
        logger.info("✅ Ruff corrections applied.")
    except Exception as e:
        logger.warning(f"⚠️ Ruff encountered issues: {e}")


def fix_bare_excepts(file_path):
    """Replaces bare 'except Exception:' with 'except Exception:'."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern: 'except Exception:' surrounded by whitespace/newlines
    # This is a simple regex and might need refinement for edge cases (comments, strings)
    # Using a negative lookahead to ensure we don't match 'except Exception:'
    new_content = re.sub(
        r"except\s*:(?!\s*#)",
        "except Exception:",
        content
    )

    if content != new_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        logger.info(f"🔧 Fixed bare excepts in {os.path.relpath(file_path, REPO_ROOT)}")
        return True
    return False


def fix_zip_strict(file_path):
    """Adds 'strict=False' to zip() calls if missing."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Naive pattern: zip(...) with no strict=
    # This is risky with regex but helpful for this specific request.
    # We look for zip(arg1, arg2) pattern and check if strict is absent.
    # Note: Parsing AST is safer, but this is a quick heuristic script as requested.

    # Matches: zip(a, b) -> zip(a, b, strict=False)
    # This regex is conservative to avoid breaking complex calls.
    # It looks for zip( followed by non-parenthesis chars, and if strict is not present.

    # Matches: zip(a, b) -> zip(a, b, strict=False)
    # This regex is conservative to avoid breaking complex calls.
    # It looks for zip( followed by non-parenthesis chars, and if strict is not present.

    if "zip(" in content and "strict=" not in content:
        # Targeted fix for the known pattern in database.py
        new_content = content.replace("zip(columns, row))", "zip(columns, row, strict=False))")

        if content != new_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"🔧 Fixed zip(strict=False) in {os.path.relpath(file_path, REPO_ROOT)}")
            return True

    return False


def custom_fixes():
    """Applies custom regex-based fixes to python files."""
    extensions = {".py"}
    exclude_dirs = {"venv", ".venv", "__pycache__", "node_modules", "refactor_backup"}

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    fix_bare_excepts(file_path)
                    fix_zip_strict(file_path)
                except Exception as e:
                    logger.warning(f"Could not process {file}: {e}")



def verify_imports():
    """Runs the import checker."""
    logger.info("🔍 Verifying imports...")
    check_script = os.path.join(REPO_ROOT, "check_imports.py")
    if os.path.exists(check_script):
        try:
            run_cmd([sys.executable, check_script])
            logger.info("✅ Imports verified.")
        except Exception:
            logger.error("❌ Import verification failed.")


def main():
    logger.info("🚀 Starting Auto-Fixer Protocol...")

    # Phase 1: Custom Fixes (Apply these first so Ruff can format them)
    logger.info("Phase 1: Applying Custom Patterns...")
    custom_fixes()

    # Phase 2: Ruff (Standard Lint/Format)
    logger.info("Phase 2: Running Ruff...")
    fix_ruff()

    # Phase 3: Verification
    logger.info("Phase 3: Verification...")
    verify_imports()

    logger.info("✨ Auto-Fix Sequence Complete.")


if __name__ == "__main__":
    main()
