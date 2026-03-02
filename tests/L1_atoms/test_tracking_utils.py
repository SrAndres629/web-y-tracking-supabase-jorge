import pytest
from app.tracking import extract_fbclid_from_fbc, get_prioritized_fbclid



@pytest.mark.parametrize(
    "fbc_cookie,expected",
    [
        # Valid cases
        ("fb.1.1696956789.myfbclid", "myfbclid"),
        ("fb.1.1696956789.myfbclid.extra", "myfbclid"),

        # Invalid prefixes
        ("test.1.123.id", None),
        ("fba.1.123.id", None),

        # Insufficient parts
        ("fb.1.123", None),
        ("fb.1.", None),
        ("fb.1", None),

        # Edge cases
        (None, None),
        ("", None),
        ("   ", None),
    ],
)
def test_extract_fbclid_from_fbc(fbc_cookie, expected):
    """Test extraction of fbclid from fbc cookie string."""
    assert extract_fbclid_from_fbc(fbc_cookie) == expected


@pytest.mark.parametrize(
    "url_fbclid,cookie_fbc,expected",
    [
        # Priority: URL > Cookie
        ("url_id", "fb.1.123.cookie_id", "url_id"),
        ("url_id", None, "url_id"),
        ("url_id", "", "url_id"),

        # Fallback to Cookie
        (None, "fb.1.123.cookie_id", "cookie_id"),
        ("", "fb.1.123.cookie_id", "cookie_id"),

        # Both missing or invalid
        (None, None, None),
        (None, "invalid.cookie", None),
        ("", "", None),
    ],
)
def test_get_prioritized_fbclid(url_fbclid, cookie_fbc, expected):
    """Test priority logic for fbclid selection."""
    assert get_prioritized_fbclid(url_fbclid, cookie_fbc) == expected
