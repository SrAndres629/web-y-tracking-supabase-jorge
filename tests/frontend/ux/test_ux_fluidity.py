import pytest
from fastapi.testclient import TestClient
from main import app
import re

client = TestClient(app)

def test_smooth_scroll_libraries_presence():
    """
    Verify that the necessary smooth scrolling libraries are included in the homepage.
    GSAP and Lenis are the 'Silicon Valley' standard for this project.
    """
    response = client.get("/")
    assert response.status_code == 200
    content = response.text

    # Check for GSAP
    assert "gsap.min.js" in content, "❌ GSAP not found in index.html"
    
    # Check for ScrollTrigger (needed for advanced parallax/reveal)
    assert "ScrollTrigger.min.js" in content, "❌ ScrollTrigger not found in index.html"

    # Check for Lenis (The Smooth Scroll Engine)
    assert "lenis.min.js" in content, "❌ Lenis not found in index.html"

def test_lenis_initialization_block():
    """
    Verify that there is a script block initializing Lenis.
    """
    response = client.get("/")
    content = response.text
    
    # Check for the initialization pattern in base.html logic
    assert "scroll-init" in content, "❌ Lenis initialization event not found in HTML"
    assert "window.lenis = lenis" in content, "❌ Lenis instance assignment not found"
    assert "requestAnimationFrame" in content, "❌ Scroll loop (requestAnimationFrame) not found"

def test_scroll_trigger_config():
    """
    Ensure ScrollTrigger is synced with Lenis if used.
    """
    response = client.get("/")
    content = response.text
    
    # Common pattern for GSAP + Lenis sync
    # lenis.on('scroll', ScrollTrigger.update)
    if "ScrollTrigger" in content and "lenis" in content.lower():
        assert "ScrollTrigger.update" in content, "⚠️ ScrollTrigger might not be synced with Lenis scroll events"

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Running UX Fluidity Integrity Checks...")
    test_smooth_scroll_libraries_presence()
    test_lenis_initialization_block()
    test_scroll_trigger_config()
    logger.info("✅ UX Fluidity Integrity Verified (Architecture Level)")
