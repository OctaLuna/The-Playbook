"""Contrato de GET /api/matches/{match_id}/prediction (001-prediccion-partido).

Grupo 1 de `specs/001-prediccion-partido/tasks.md` (T004) — fase Red del
Artículo III: `backend/app/api/` todavía no existe (Grupo 2-3).

Igual que `test_match_detail.py`: solo se prueba la forma del caso 200 con un
`match_id` de ejemplo. El caso 404 ("sin predicción generada") se difiere a
Grupo 4 (T017+), cuando exista `Predicción` (T008) real para sembrar y
distinguir "partido sin predicción" de "ruta inexistente".

`top_shap_features` NO debe aparecer en el body (nota explícita del
contrato) — es un campo interno para 002, no se expone en este endpoint.

AVISO para quien implemente T015 (mismo caso que `test_match_detail.py`):
el test de abajo va a volver a fallar apenas exista el router real, porque
sin `Partido`/`Predicción` sembrados un UUID al azar debe dar 404 legítimo,
no 200. Necesita reescritura con datos reales, no un ajuste menor.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract


async def test_match_prediction_devuelve_forma_del_contrato(client: AsyncClient) -> None:
    """RF-001, RF-002, RF-003, RF-004, RF-005."""
    match_id = uuid4()
    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 200
    body = response.json()

    for campo in (
        "match_id",
        "probabilities_1x2",
        "over_under_2_5",
        "btts",
        "xg",
        "confidence",
        "head_to_head_available",
        "low_data_warning",
        "model_version",
        "generated_at",
    ):
        assert campo in body

    assert "top_shap_features" not in body
