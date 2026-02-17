import os

import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.skipif(
    os.getenv("CI") is None and os.getenv("SMOKE_TEST") is None,
    reason="Smoke tests only run if CI or SMOKE_TEST=1 is set",
)
def test_production_smoke_200():
    """
    SMOKE TEST: Verifies that the production (or provided URL) returns 200 OK
    and renders the main headline.
    """
    target_url = os.getenv("TARGET_URL", "https://jorgeaguirreflores.com")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        response = page.goto(target_url, timeout=30000)

        # 1. Check HTTP Status
        assert response.status == 200, (
            f"🔥 Smoke Test Failed: {target_url} returned {response.status}"
        )

        # 2. Check for critical content (Hero section)
        # Assuming "30 AÑOS" or "Jorge Aguirre Flores" is always there
        content = page.content()
        assert "Jorge Aguirre Flores" in content, (
            "🔥 Smoke Test Failed: Critical branding missing from page."
        )

        # 3. Check for specific element (E.g. Agendar button)
        # Using .first to avoid strict mode violation if multiple buttons exist
        agendar_button = page.locator("text=Agendar").first
        assert agendar_button.is_visible(), "🔥 Smoke Test Failed: 'Agendar' button not visible."

        browser.close()


def test_local_smoke_200():
    """
    SMOKE TEST: Verifies local server stability.
    """
    # This expects the server to be running or we use a fixture to start it.
    # For now, we skip or target a local dev port if specified.
    local_url = os.getenv("LOCAL_URL")
    if not local_url:
        pytest.skip("LOCAL_URL not provided.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(local_url)
        assert response.status == 200
        browser.close()
