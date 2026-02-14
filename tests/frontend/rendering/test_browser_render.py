import pytest
import os
import requests
from playwright.sync_api import sync_playwright

def test_frontend_full_render():
    """
    HIGH-FIDELITY E2E: Verifies the frontend renders correctly in a REAL browser.
    Checks for:
    1. HTTP 200 Security
    2. Zero console errors (JS integrity)
    3. CSS/Layout availability (Agendar button visibility)
    4. Meta Pixel Injection (Ad-Tech contract)
    """
    target_url = os.getenv("TARGET_URL", "http://localhost:8000") # Default to local
    if "localhost" in target_url or "127.0.0.1" in target_url:
        try:
            requests.get(target_url, timeout=2)
        except requests.RequestException:
            pytest.skip(f"Local target is not running: {target_url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Track console errors to ensure no JS breakage
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            response = page.goto(target_url, wait_until="networkidle")
            
            # 1. Status Code
            assert response.status == 200, f"🔥 Frontend failed to load: {response.status}"
            
            # 2. NO CRITICAL JS ERRORS
            # Filter typical non-breaking warnings or known third-party noises if needed
            assert not console_errors, f"🔥 Critical JS Errors found in frontend: {console_errors}"
            
            # 3. VISUAL INTEGRITY (CSS Check)
            # Using .first because we have multiple buttons as confirmed in previous audit
            agendar_btn = page.locator("text=Agendar").first
            assert agendar_btn.is_visible(), "🔥 Layout broken: Primary CTA 'Agendar' is NOT visible in browser."
            
            # 4. MARKETING CONTRACT (Meta Pixel)
            # We check the page source after JS execution to see if the pixel script is there
            content = page.content()
            # Pixel IDs usually match a pattern
            assert "connect.facebook.net" in content, "🔥 Ad-Tech Breach: Meta Pixel library NOT detected."
            
            browser.close()
    except Exception as exc:
        msg = str(exc).lower()
        if isinstance(exc, PermissionError) or "winerror 5" in msg or "access is denied" in msg:
            pytest.skip(f"Playwright blocked by runtime permissions: {exc}")
        if "err_connection_refused" in msg:
            pytest.skip(f"Target URL unreachable for browser test: {target_url}")
        raise
