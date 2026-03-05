import re

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_footer_social_links_a11y():
    """
    Verify that icon-only social links in the footer have aria-label attributes.
    """
    response = client.get("/")
    assert response.status_code == 200

    html = response.text

    # We want to check specifically in the footer section.
    # While it's easier to use BeautifulSoup, we will stick to memory's suggestion to use `re`
    # for lightweight HTML parsing to find the anchor tags around social icons in the footer.

    # Extract the footer tag content
    footer_match = re.search(r"<footer.*?>(.*?)</footer>", html, flags=re.DOTALL)
    assert footer_match is not None, "Footer tag not found"

    footer_html = footer_match.group(1)

    # Find all anchor tags that contain an <i> tag (likely icon-only links)
    icon_links = re.findall(
        r'<a\s+[^>]*>.*?<i\s+[^>]*class=["\']fab fa-[^>]*>.*?</i>.*?</a>',
        footer_html,
        flags=re.DOTALL,
    )

    assert len(icon_links) >= 3, (
        f"Expected at least 3 social links with icons in footer, found {len(icon_links)}"
    )

    for link_html in icon_links:
        # Check if aria-label exists on the anchor tag
        has_aria_label = re.search(r'aria-label=["\'][^"\']+["\']', link_html)
        assert has_aria_label is not None, (
            f"Missing aria-label on icon-only link: {link_html.strip()}"
        )


def test_mobile_menu_close_button_a11y():
    """
    Verify that the mobile menu close button has an aria-label attribute.
    """
    response = client.get("/")
    assert response.status_code == 200

    html = response.text

    # Extract the #mobileMenu div
    mobile_menu_match = re.search(
        r'<div[^>]*id="mobileMenu"[^>]*>(.*?)</div>', html, flags=re.DOTALL
    )
    assert mobile_menu_match is not None, "mobileMenu not found"

    menu_html = mobile_menu_match.group(1)

    # The close button contains &times;
    close_button_match = re.search(
        r"<button[^>]*>.*?&times;.*?</button>", menu_html, flags=re.DOTALL
    )
    assert close_button_match is not None, "Close button not found in mobile menu"

    close_button_html = close_button_match.group(0)
    has_aria_label = re.search(r'aria-label=["\'][^"\']+["\']', close_button_html)
    assert has_aria_label is not None, (
        f"Missing aria-label on mobile menu close button: {close_button_html.strip()}"
    )
