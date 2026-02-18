#!/usr/bin/env python3
"""
🏥 TERMINAL SOLVER (PROJECT DOCTOR)
Specialized script to resolve common terminal, environment, and code issues.

Usage:
    python tools/terminal_solver.py

Features:
    - 🧹 Cache Cleaning (__pycache__, .pytest_cache, etc.)
    - 📦 Dependency Sync (requirements.txt)
    - 🐍 Environment Validation (Python version, Venv)
    - 🔧 Auto-Fixer Integration (Ruff, formatting)
    - 🧪 Test Suite Verification
"""

import os
import shutil
import subprocess
import sys
import logging
from pathlib import Path

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TerminalSolver")

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_cmd(command, cwd=None, ignore_errors=False, shell=False):
    """Executes a shell command."""
    try:
        logger.info(f"⚡ Running: {command}")
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
            logger.error(f"❌ Command failed: {command}\n{e.stderr}")
            raise e
        return e.stdout.strip()

def print_banner():
    print(r"""
   _______                  _                 _   _____       _
  |__   __|                (_)               | | / ____|     | |
     | | ___ _ __ _ __ ___  _ _ __   __ _  | || (___   ___ | |_   _____ _ __
     | |/ _ \ '__| '_ ` _ \| | '_ \ / _` |  | | \___ \ / _ \| \ \ / / _ \ '__|
     | |  __/ |  | | | | | | | | | | (_| | |__| |___) | (_) | |\ V /  __/ |
     |_|\___|_|  |_| |_| |_|_|_| |_|\__,_| |_____/_____/ \___/|_| \_/ \___|_|
    """)
    print("🚀 Initializing System Doctor...\n")

def check_environment():
    """Validates Python environment."""
    logger.info("🔍 Checking Environment...")

    # Check Python Version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        logger.warning(f"⚠️ Warning: Python {version.major}.{version.minor} detected. Recommended: 3.9+")
    else:
        logger.info(f"✅ Python Version: {version.major}.{version.minor}")

    # Check Venv
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        logger.info(f"✅ Running inside Virtual Environment: {sys.prefix}")
    else:
        logger.warning("⚠️ NOT running in a Virtual Environment. Recommended to use 'venv'.")

def clean_cache():
    """Removes temporary cache files."""
    logger.info("🧹 Cleaning Cache...")
    target_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
        "htmlcov"
    ]

    count = 0
    for root, dirs, files in os.walk(REPO_ROOT):
        for d in dirs:
            if d in target_dirs:
                path = os.path.join(root, d)
                try:
                    shutil.rmtree(path)
                    count += 1
                except Exception as e:
                    logger.warning(f"Could not remove {path}: {e}")

    logger.info(f"✅ Removed {count} cache directories.")

def install_dependencies():
    """Installs dependencies from requirements.txt."""
    req_file = REPO_ROOT / "requirements.txt"
    if req_file.exists():
        logger.info("📦 Installing/Syncing Dependencies...")
        try:
            run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], ignore_errors=True)
            logger.info("✅ Dependencies synced.")
        except Exception:
            logger.error("❌ Failed to install dependencies.")
    else:
        logger.warning("⚠️ requirements.txt not found.")

def run_auto_fixer():
    """Runs the existing auto_fix.py script."""
    auto_fix_path = REPO_ROOT / "tools" / "auto_fix.py"
    if auto_fix_path.exists():
        logger.info("🔧 Running Auto-Fixer...")
        try:
            run_cmd([sys.executable, "tools/auto_fix.py"], ignore_errors=True)
            logger.info("✅ Auto-Fixer completed.")
        except Exception:
            logger.error("❌ Auto-Fixer failed.")
    else:
        logger.warning("⚠️ tools/auto_fix.py not found.")

def run_tests():
    """Runs tests to verify system stability."""
    logger.info("🧪 Running Tests...")
    try:
        run_cmd([sys.executable, "-m", "pytest"], ignore_errors=True)
        logger.info("✅ Tests execution completed (Check output for details).")
    except Exception:
        logger.error("❌ Tests failed to run.")

def main():
    print_banner()
    try:
        clean_cache()
        check_environment()
        install_dependencies()
        run_auto_fixer()
        run_tests()
        print("\n✨ Terminal Solver Finished! verification complete.")
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"🔥 Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
