from fastapi.testclient import TestClient
from main import app
import re

client = TestClient(app)

def test_footer_social_links_have_aria_labels():
    """
    Verify that social media links in the footer have aria-label attributes for accessibility.
    """
    response = client.get("/")
    assert response.status_code == 200
    content = response.text

    # Social media URLs to check
    social_urls = [
        "https://www.facebook.com/jorgeaguirreflores",
        "https://www.instagram.com/jorgeaguirreflores",
        "https://www.tiktok.com/@jorgeaguirreflores"
    ]

    for url in social_urls:
        # Construct a regex to find the anchor tag containing the URL
        # We look for <a ... href="URL" ...>
        # This is a bit brittle but works without BeautifulSoup

        # Check if the link exists
        assert url in content, f"Link to {url} not found in response"

        # Check if it has an aria-label
        # We search for the specific link and check if aria-label is present in its tag
        # The regex looks for <a [anything] href="URL" [anything] aria-label="[anything]"
        # or <a [anything] aria-label="[anything]" [anything] href="URL"

        # Simplified check: Find the tag string
        # This assumes the href is unique enough or we can find the specific block

        # Let's try to find the specific lines or block
        # We can just check if there is an aria-label associated with the link.

        # A more robust regex might be needed if the order of attributes varies,
        # but for this specific template, we know the structure.
        # However, to be safe and "black-box", let's try to match the tag content.

        # Pattern to match the whole anchor tag: <a [^>]*href="url"[^>]*>
        pattern = fr'<a[^>]*href="{re.escape(url)}"[^>]*>'
        match = re.search(pattern, content)

        assert match is not None, f"Could not find anchor tag for {url}"
        tag_content = match.group(0)

        assert "aria-label=" in tag_content, f"aria-label missing for {url}. Tag: {tag_content}"
