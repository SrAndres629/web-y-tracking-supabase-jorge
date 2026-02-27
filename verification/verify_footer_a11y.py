from playwright.sync_api import sync_playwright

def verify_footer_a11y():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            print("Navigating to homepage...")
            # Using the local server we should start
            page.goto("http://localhost:8000")
            print("Page loaded.")

            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Verify aria-labels
            print("Verifying aria-labels...")

            fb = page.locator('a[href*="facebook.com"]')
            fb_label = fb.get_attribute("aria-label")
            print(f"Facebook: {fb_label}")
            assert fb_label == "Síguenos en Facebook"

            ig = page.locator('a[href*="instagram.com"]')
            ig_label = ig.get_attribute("aria-label")
            print(f"Instagram: {ig_label}")
            assert ig_label == "Síguenos en Instagram"

            tt = page.locator('a[href*="tiktok.com"]')
            tt_label = tt.get_attribute("aria-label")
            print(f"TikTok: {tt_label}")
            assert tt_label == "Síguenos en TikTok"

            # Take screenshot
            footer = page.locator("footer")
            footer.screenshot(path="verification/footer_verification.png")
            print("Screenshot saved.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_footer_a11y()
