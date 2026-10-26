"""Browser CORS contract for the local Next.js frontend."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.contract


@pytest_asyncio.fixture
async def cors_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_local_frontend_can_read_api(cors_client: AsyncClient) -> None:
    response = await cors_client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.parametrize("method", ["GET", "POST"])
async def test_local_frontend_preflight_allows_api_methods(
    cors_client: AsyncClient, method: str
) -> None:
    response = await cors_client.options(
        "/api/matches/upcoming",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert method in response.headers["access-control-allow-methods"]


async def test_unknown_origin_is_not_allowed(cors_client: AsyncClient) -> None:
    response = await cors_client.get("/health", headers={"Origin": "https://attacker.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
