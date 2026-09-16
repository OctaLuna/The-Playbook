"""Contrato de GET /api/matches/{match_id} (001-prediccion-partido).

Grupo 1 de `specs/001-prediccion-partido/tasks.md` (T003) — fase Red del
Artículo III: `backend/app/api/` todavía no existe (Grupo 2-3).

Solo se prueba la forma del caso 200 con un `match_id` de ejemplo. El caso
404 ("partido inexistente", que la tarea menciona) NO se incluye acá a
propósito: sin el modelo `Partido` (T006) todavía no hay forma de sembrar un
partido real en Postgres, así que ahora mismo *cualquier* UUID devolvería 404
— pero por la ruta inexistente, no por la lógica real de "partido no
encontrado". Escribir ese test ahora daría un verde falso en cuanto exista el
router, sin haber verificado nada. Se agrega en Grupo 4 (T017+) una vez que
haya un `Partido` real que sembrar para distinguir ambos casos.

AVISO para quien implemente T015: el test de abajo (200 con UUID sin
sembrar) se va a romper de nuevo apenas exista el router real, pero por una
razón distinta y legítima — sin un `Partido` sembrado, `GET
/api/matches/{uuid4()}` debe devolver 404 de verdad, no 200. No es un bug de
T015; es que este test necesita reescritura (fixture con `Partido` real
insertado vía `db_session`), no solo un ajuste menor.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract


async def test_match_detail_devuelve_forma_del_contrato(client: AsyncClient) -> None:
    """RF-006: id/league/home_team/away_team/kickoff_at/status/real_result."""
    match_id = uuid4()
    response = await client.get(f"/api/matches/{match_id}")

    assert response.status_code == 200
    body = response.json()

    for campo in (
        "id",
        "league",
        "home_team",
        "away_team",
        "kickoff_at",
        "status",
        "real_result",
    ):
        assert campo in body
