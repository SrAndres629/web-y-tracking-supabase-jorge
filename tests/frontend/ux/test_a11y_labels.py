from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
from main import app

client = TestClient(app)

def test_mobile_menu_close_button_a11y():
    """
    Verify that the mobile menu close button has an aria-label.
    """
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    # The close button is inside #mobileMenu
    mobile_menu = soup.find(id="mobileMenu")
    assert mobile_menu is not None, "Mobile menu not found"

    # Find the button that closes the menu. It contains &times;
    close_btn = None
    for btn in mobile_menu.find_all("button"):
        if "&times;" in str(btn) or "×" in btn.get_text():
            close_btn = btn
            break

    assert close_btn is not None, "Mobile menu close button not found"
    assert close_btn.has_attr("aria-label"), "Mobile menu close button missing aria-label"
    assert close_btn["aria-label"] != "", "Mobile menu close button aria-label is empty"

def test_footer_social_links_a11y():
    """
    Verify that social media links in the footer have aria-labels.
    """
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    footer = soup.find("footer")
    assert footer is not None, "Footer not found"

    # Find links to facebook, instagram, tiktok
    social_platforms = ["facebook", "instagram", "tiktok"]

    for platform in social_platforms:
        # Find <a> tags that contain the platform name in href
        link = footer.find("a", href=lambda href: href and platform in href)
        assert link is not None, f"Link for {platform} not found in footer"

        assert link.has_attr("aria-label"), f"{platform} link missing aria-label"
        assert link["aria-label"] != "", f"{platform} link aria-label is empty"
