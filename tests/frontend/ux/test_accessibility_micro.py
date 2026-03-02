from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_footer_social_links_accessibility():
    """
    Verify that social media links in the footer have aria-labels.
    This ensures accessibility for screen readers on icon-only links.
    """
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    # Footer social links
    facebook_link = soup.find("a", href="https://www.facebook.com/jorgeaguirreflores")
    assert facebook_link is not None, "❌ Facebook link not found"
    assert facebook_link.get("aria-label") == "Facebook", "❌ Facebook link missing correct aria-label"

    instagram_link = soup.find("a", href="https://www.instagram.com/jorgeaguirreflores")
    assert instagram_link is not None, "❌ Instagram link not found"
    assert instagram_link.get("aria-label") == "Instagram", "❌ Instagram link missing correct aria-label"

    tiktok_link = soup.find("a", href="https://www.tiktok.com/@jorgeaguirreflores")
    assert tiktok_link is not None, "❌ TikTok link not found"
    assert tiktok_link.get("aria-label") == "TikTok", "❌ TikTok link missing correct aria-label"


def test_mobile_menu_close_button_accessibility():
    """
    Verify that the mobile menu close button has an aria-label.
    """
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    # Mobile menu close button
    # We find it by its onclick content since it doesn't have a unique ID,
    # but it's inside #mobileMenu
    mobile_menu = soup.find("div", id="mobileMenu")
    assert mobile_menu is not None, "❌ Mobile menu container not found"

    close_button = mobile_menu.find("button", {"aria-label": "Cerrar menú"})
    assert close_button is not None, "❌ Mobile menu close button with aria-label not found"
    # BeautifulSoup decodes &times; to ×
    assert "×" in close_button.text or "&times;" in close_button.decode_contents(), "❌ Close button content mismatch"

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("🚀 Running Accessibility Micro-Checks...")
    test_footer_social_links_accessibility()
    test_mobile_menu_close_button_accessibility()
    logger.info("✅ Accessibility Micro-Checks Verified")
