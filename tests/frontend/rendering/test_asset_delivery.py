import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_static_css_and_js_are_served_with_valid_types():
    """
    Prevents regressions where production serves plain HTML without styles/scripts.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        css = await client.get("/static/dist/css/app.min.css")
        js = await client.get("/static/engines/tracking/index.js")

    assert css.status_code == 200, f"Missing CSS asset: {css.status_code}"
    assert "text/css" in (css.headers.get("content-type", "")), css.headers.get("content-type")
    assert css.text and not css.text.lstrip().lower().startswith("<!doctype html>")

    assert js.status_code == 200, f"Missing JS asset: {js.status_code}"
    assert "javascript" in (js.headers.get("content-type", "")), js.headers.get("content-type")
    assert js.text and not js.text.lstrip().lower().startswith("<!doctype html>")
