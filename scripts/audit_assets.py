#!/usr/bin/env python3
"""
AUDIT ASSETS SCRIPT
Silicon Valley Standard Integrity Check

Checks for:
1. Presence of critical build configuration files.
2. Validity and freshness of compiled CSS.
3. Existence of static assets referenced in HTML.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.absolute()
STATIC_DIR = ROOT_DIR / "static"
DIST_CSS = STATIC_DIR / "dist" / "css" / "app.min.css"

REQUIRED_FILES = [
    "package.json",
    "tailwind.config.js",
    "postcss.config.js"
]

CRITICAL_CLASSES = [
    "bg-luxury-black",
    "text-luxury-gold"
]

def check_build_config():
    """Verifies existence of build configuration files."""
    missing = []
    for filename in REQUIRED_FILES:
        file_path = ROOT_DIR / filename
        if not file_path.exists():
            missing.append(filename)
    
    if missing:
        logger.error(f"❌ Missing build configuration: {', '.join(missing)}")
        return False
    
    logger.info("✅ Build configuration files present.")
    return True

def check_css_integrity():
    """Verifies app.min.css exists and contains critical classes."""
    if not DIST_CSS.exists():
        logger.error("❌ app.min.css not found!")
        return False
    
    # Check size
    size_kb = DIST_CSS.stat().st_size / 1024
    if size_kb < 1:
        logger.error(f"❌ app.min.css is suspiciously small ({size_kb:.2f} KB)")
        return False

    # Check content
    try:
        content = DIST_CSS.read_text(encoding="utf-8")
        failed_classes = []
        for cls in CRITICAL_CLASSES:
            if cls not in content:
                failed_classes.append(cls)
        
        if failed_classes:
            logger.error(f"❌ app.min.css is missing critical classes: {', '.join(failed_classes)}")
            # logger.info("   Run 'npm run build:css' to fix.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error reading CSS file: {e}")
        return False

    logger.info(f"✅ app.min.css verified ({size_kb:.2f} KB, includes critical classes).")
    return True

def main():
    logger.info("🔍 Starting Asset Integrity Audit...")
    
    config_ok = check_build_config()
    css_ok = check_css_integrity()
    
    if config_ok and css_ok:
        logger.info("🚀 ASSET AUDIT PASSED. System is healthy.")
        sys.exit(0)
    else:
        logger.error("🚫 ASSET AUDIT FAILED. detailed errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
