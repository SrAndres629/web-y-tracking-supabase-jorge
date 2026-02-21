import os
from playwright.sync_api import sync_playwright

def capture_screenshot():
    print("Initializing Playwright Engine...")
    with sync_playwright() as p:
        try:
            print("Launching Chromium...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Navigating to production deployment: https://jorgeaguirreflores.com/")
            page.goto("https://jorgeaguirreflores.com/")
            
            # Wait for any animations to finish
            page.wait_for_timeout(3000)
            
            output_path = "/home/jorand/.gemini/antigravity/brain/ac633f48-2ef2-4d61-a8bf-6abacfe3b6e6/proof_restored_ui.png"
            print(f"Bypassing Subagent API. Saving forensic image to: {output_path}")
            
            page.screenshot(path=output_path, full_page=True)
            browser.close()
            print("Screenshot captured successfully. Visual proof acquired.")
        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")

if __name__ == "__main__":
    capture_screenshot()
