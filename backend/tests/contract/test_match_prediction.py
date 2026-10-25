"""Contrato de GET /api/matches/{match_id}/prediction (001-prediccion-partido)."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract


async def test_match_prediction_inexistente_devuelve_404(client: AsyncClient) -> None:
    response = await client.get(f"/api/matches/{uuid4()}/prediction")

    assert response.status_code == 404
