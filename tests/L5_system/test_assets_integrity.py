
import pytest
import os
import logging
from pathlib import Path

# 🛡️ SILICON VALLEY STANDARD INTEGRITY CHECK
# Replaces legacy scripts/audit_assets.py

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
# This test runs in tests/L5_system/, so we go up 3 levels to root
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
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

@pytest.mark.L5
@pytest.mark.audit
def test_build_config_exists():
    """Verifies existence of critical build configuration files."""
    missing = []
    for filename in REQUIRED_FILES:
        file_path = ROOT_DIR / filename
        if not file_path.exists():
            missing.append(filename)
    
    if missing:
        pytest.fail(f"❌ Missing build configuration: {', '.join(missing)}")
    
    print("✅ Build configuration files present.")

@pytest.mark.L5
@pytest.mark.audit
def test_css_integrity():
    """Verifies app.min.css exists, has size, and contains critical classes."""
    if not DIST_CSS.exists():
        pytest.fail("❌ app.min.css not found! Run 'npm run build:css'")
    
    # Check size
    size_kb = DIST_CSS.stat().st_size / 1024
    if size_kb < 1:
        pytest.fail(f"❌ app.min.css is suspiciously small ({size_kb:.2f} KB)")

    # Check content
    try:
        content = DIST_CSS.read_text(encoding="utf-8")
        failed_classes = []
        for cls in CRITICAL_CLASSES:
            if cls not in content:
                failed_classes.append(cls)
        
        if failed_classes:
            pytest.fail(f"❌ app.min.css is missing critical classes: {', '.join(failed_classes)}")
            
    except Exception as e:
        pytest.fail(f"❌ Error reading CSS file: {e}")

    print(f"✅ app.min.css verified ({size_kb:.2f} KB, includes critical classes).")
