#!/usr/bin/env python3
"""
🏥 PROJECT DOCTOR - The Definitive Self-Healing Script
Consolidates Ruff, Mypy, and Custom checks into a single report.
Returns non-zero exit code if any issues remain.
"""

import logging
import os
import re
import subprocess
import sys
from pathlib import Path

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ProjectDoctor")

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = os.path.join(REPO_ROOT, "venv", "bin", "python3")
RUFF_EXE = os.path.join(REPO_ROOT, "venv", "bin", "ruff")
MYPY_EXE = os.path.join(REPO_ROOT, "venv", "bin", "mypy")


def run_check(name, command):
    """Runs a check and returns (is_clean, output)."""
    logger.info(f"🔍 Running {name}...")
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        is_clean = result.returncode == 0
        return is_clean, result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to run {name}: {e}")
        return False, str(e)


def check_css_typos():
    """Custom sweep for CSS issues and common typos."""
    logger.info("🎨 Checking CSS and Typos...")
    issues = []

    # CSS: Empty rulesets
    css_files = list(REPO_ROOT.glob("**/*.css"))
    for css_file in css_files:
        if any(
            x in str(css_file)
            for x in ["venv", "node_modules", ".vercel", ".ruff_cache"]
        ):
            continue
        with open(css_file, "r") as f:
            content = f.read()
            # Find empty rulesets: .name { }
            if re.search(r"\{\s*\}", content):
                issues.append(
                    f"Empty ruleset found in {css_file.relative_to(REPO_ROOT)}"
                )

    # Typos: Common Spanish leftovers in comments
    patterns = [
        (r"\bClases\b", "Classes"),
        (r"\bComponentes\b", "Components"),
    ]

    ignore_dirs = {
        "venv",
        ".venv",
        ".git",
        "__pycache__",
        ".vercel",
        ".ai",
        "refactor_backup",
        ".ruff_cache",
        ".mypy_cache",
        "node_modules",
    }

    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip ignore_dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith((".py", ".css", ".md")):
                file_path = Path(root) / file
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                    for pattern, _ in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append(
                                f"Typo/Spanish leftover '{pattern}' found in "
                                f"{file_path.relative_to(REPO_ROOT)}"
                            )

    return len(issues) == 0, "\n".join(issues)


def main():
    print("\n" + "=" * 60)
    print("      🏥 PROJECT DOCTOR - HEALTH CHECK")
    print("=" * 60 + "\n")

    total_issues = 0

    # 1. Ruff Check
    ruff_clean, ruff_out = run_check("Ruff", [RUFF_EXE, "check", "."])
    if not ruff_clean:
        print(f"\n❌ RUFF DETECTED ISSUES:\n{ruff_out}")
        total_issues += 1
    else:
        print("✅ Ruff: Clean")

    # 2. Mypy Check
    if os.path.exists(MYPY_EXE):
        mypy_clean, mypy_out = run_check(
            "Mypy", [MYPY_EXE, "--ignore-missing-imports", "."]
        )
        if not mypy_clean:
            print(f"\n❌ MYPY DETECTED ISSUES:\n{mypy_out}")
            total_issues += 1
        else:
            print("✅ Mypy: Clean")
    else:
        logger.warning(f"⚠️ Mypy not found at {MYPY_EXE}")

    # 3. CSS & Typos
    css_clean, css_out = check_css_typos()
    if not css_clean:
        print(f"\n❌ CSS/TYPOS DETECTED ISSUES:\n{css_out}")
        total_issues += 1
    else:
        print("✅ CSS/Typos: Clean")

    print("\n" + "=" * 60)
    if total_issues == 0:
        print("✨ RESULT: PROJECT IS HEALTHY!")
        sys.exit(0)
    else:
        print(f"💔 RESULT: {total_issues} ENGINE(S) REPORTED PROBLEMS.")
        sys.exit(1)


if __name__ == "__main__":
    main()
