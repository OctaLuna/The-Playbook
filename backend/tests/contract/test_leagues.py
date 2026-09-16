"""Contrato de GET /api/leagues (001-prediccion-partido).

Grupo 1 de `specs/001-prediccion-partido/tasks.md` (T001) — fase Red del
Artículo III: `backend/app/api/` todavía no existe (Grupo 2-3), así que esta
prueba debe fallar ahora por eso, no por otra razón.

Las 5 ligas son un enum fijo (`Partido.liga`, T006), no una tabla — no hace
falta seed de datos en Postgres para verificar este contrato.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract

LIGAS_ESPERADAS = {
    "premier_league": "Premier League",
    "laliga": "LaLiga",
    "serie_a": "Serie A",
    "bundesliga": "Bundesliga",
    "ligue_1": "Ligue 1",
}


async def test_leagues_devuelve_las_5_ligas_cubiertas(client: AsyncClient) -> None:
    """RF-008: lista fija de las 5 ligas del MVP, con id y name."""
    response = await client.get("/api/leagues")

    assert response.status_code == 200
    body = response.json()

    assert "leagues" in body
    ligas = {liga["id"]: liga["name"] for liga in body["leagues"]}
    assert ligas == LIGAS_ESPERADAS
