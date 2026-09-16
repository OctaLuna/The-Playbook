"""Contrato de GET /api/matches/upcoming (001-prediccion-partido).

Grupo 1 de `specs/001-prediccion-partido/tasks.md` (T002) — fase Red del
Artículo III: `backend/app/api/` todavía no existe (Grupo 2-3).

Sin seed de datos (el modelo `Partido` de T006 todavía no existe), esta fase
solo verifica la forma de la respuesta de `contracts/matches-api.md` — el
endpoint puede responder con `matches: []` legítimamente si no hay partidos
próximos, así que no hace falta un `Partido` real para validar el contrato.
Los escenarios con partidos reales se cubren en Grupo 4 (T017+).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract


async def test_matches_upcoming_devuelve_forma_paginada(client: AsyncClient) -> None:
    """RF-008: matches/page/page_size/total, aunque no haya partidos todavía."""
    response = await client.get("/api/matches/upcoming")

    assert response.status_code == 200
    body = response.json()

    assert "matches" in body
    assert isinstance(body["matches"], list)
    assert "page" in body
    assert "page_size" in body
    assert "total" in body


async def test_matches_upcoming_acepta_filtro_de_liga(client: AsyncClient) -> None:
    """RF-008: filtrable por `league` sin romper el contrato de forma."""
    response = await client.get("/api/matches/upcoming", params={"league": "premier_league"})

    assert response.status_code == 200
    body = response.json()
    assert "matches" in body


async def test_matches_upcoming_acepta_paginacion(client: AsyncClient) -> None:
    """RF-008: `page`/`page_size` se reflejan en la respuesta."""
    response = await client.get("/api/matches/upcoming", params={"page": 1, "page_size": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 10
