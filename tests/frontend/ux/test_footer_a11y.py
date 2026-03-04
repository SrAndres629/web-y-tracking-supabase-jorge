import re
from pathlib import Path


def test_footer_social_links_have_aria_labels():
    """
    Ensures that social links in the footer have aria-labels for accessibility.
    We check the raw template text using re to avoid heavy dependencies.
    """
    footer_path = Path("api/templates/components/footer.html")
    assert footer_path.exists(), "Footer component template not found"

    html_content = footer_path.read_text(encoding="utf-8")

    # Check for Facebook link
    fb_match = re.search(r'<a\s+[^>]*href="[^"]*facebook\.com[^"]*"[^>]*aria-label="Facebook"[^>]*>', html_content, re.IGNORECASE)
    assert fb_match is not None, "Facebook social link is missing aria-label='Facebook'"

    # Check for Instagram link
    ig_match = re.search(r'<a\s+[^>]*href="[^"]*instagram\.com[^"]*"[^>]*aria-label="Instagram"[^>]*>', html_content, re.IGNORECASE)
    assert ig_match is not None, "Instagram social link is missing aria-label='Instagram'"

    # Check for TikTok link
    tiktok_match = re.search(r'<a\s+[^>]*href="[^"]*tiktok\.com[^"]*"[^>]*aria-label="TikTok"[^>]*>', html_content, re.IGNORECASE)
    assert tiktok_match is not None, "TikTok social link is missing aria-label='TikTok'"
