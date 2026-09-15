"""Contrato de la API pública de Track Record (003-track-record-publico).

Grupo 1 de `specs/003-track-record-publico/tasks.md` (T001, T002, T002b) — fase
Red del Artículo III: los routers de `backend/app/api/track_record.py` todavía
no existen (bloqueados por T004-T012, Grupo 2 y 3 de 003).

Sin seed de datos (los modelos `EvaluaciónPredicción`/`TrackRecordAgregado`/
`CuotaMercado` no existen todavía), esta fase solo verifica la forma de la
respuesta pública de `contracts/track-record-api.md`. Los valores agregados
reales se verifican en las pruebas de integración del Grupo 4 (T013+).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract

MERCADOS_ESPERADOS = {"1x2", "over_under_2_5", "btts"}


async def test_track_record_devuelve_las_tres_entradas_de_markets(client: AsyncClient) -> None:
    """RF-001, RF-002, RF-006: agregado global con los 3 mercados, cada uno con
    hit_rate, avg_brier_score, avg_log_loss y el baseline de mercado."""
    response = await client.get("/api/track-record")

    assert response.status_code == 200
    body = response.json()

    assert body["window_size"] == 50
    assert {m["market"] for m in body["markets"]} == MERCADOS_ESPERADOS
    for mercado in body["markets"]:
        for campo in (
            "hit_rate",
            "avg_brier_score",
            "avg_log_loss",
            "avg_market_log_loss",
            "market_baseline_matches",
        ):
            assert campo in mercado


async def test_track_record_acepta_filtro_de_liga(client: AsyncClient) -> None:
    """RF-007: filtrable por liga."""
    response = await client.get("/api/track-record", params={"league": "premier_league"})

    assert response.status_code == 200
    assert response.json()["league"] == "premier_league"


async def test_track_record_sin_filtro_devuelve_agregado_global(client: AsyncClient) -> None:
    response = await client.get("/api/track-record")

    assert response.status_code == 200
    assert response.json()["league"] is None


async def test_track_record_matches_pagina_y_filtra_por_liga(client: AsyncClient) -> None:
    """RF-003, RF-007."""
    response = await client.get(
        "/api/track-record/matches",
        params={"league": "premier_league", "page": 1, "page_size": 20},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert "matches" in body
    assert "total" in body


async def test_track_record_matches_sin_filtro_de_liga_tambien_pagina(client: AsyncClient) -> None:
    response = await client.get("/api/track-record/matches")

    assert response.status_code == 200
    body = response.json()
    assert "page" in body
    assert "page_size" in body


async def test_ninguna_respuesta_expone_cuotas_individuales_por_casa_de_apuestas(
    client: AsyncClient,
) -> None:
    """RF-005 (Artículo V): solo el agregado avg_market_log_loss, nunca una cuota
    individual (ej. bookmaker_odds, B365H) — hallazgo #5 de Analyze."""
    prohibidos = {"bookmaker_odds", "odds", "b365h", "b365d", "b365a", "cuota", "cuotas"}

    for ruta in ("/api/track-record", "/api/track-record/matches"):
        respuesta = await client.get(ruta)
        assert respuesta.status_code == 200
        cuerpo = respuesta.text.lower()
        for termino in prohibidos:
            assert termino not in cuerpo, f"{ruta} expone {termino!r}"
