import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_health_assets_endpoint_reports_runtime_assets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health/assets")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "ok"
    assert all(payload["assets"].values()), payload
