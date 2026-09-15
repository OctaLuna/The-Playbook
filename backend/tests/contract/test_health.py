import pytest
from httpx import AsyncClient


@pytest.mark.contract
async def test_health_returns_200_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
