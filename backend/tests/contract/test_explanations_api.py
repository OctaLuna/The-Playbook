"""
Contrato de la API de Explicaciones en Lenguaje Natural (002-explicacion-lenguaje-natural).

Grupo 1 de `specs/002-explicacion-lenguaje-natural/tasks.md` (T002, T003)
— fase Red del Artículo III:
Verifica el cumplimiento del contrato definido en `contracts/explanations-api.md`.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.contract


async def test_get_explanation_match_not_found(client: AsyncClient) -> None:
    """T002: Retorna 404 si el partido no existe o no tiene predicción cargada."""
    random_match_id = uuid4()
    response = await client.get(f"/api/matches/{random_match_id}/explanation")

    assert response.status_code == 404


async def test_post_follow_up_without_previous_explanation(client: AsyncClient) -> None:
    """T003: Retorna 404 si intenta hacer una pregunta de seguimiento sin explicación previa."""
    random_match_id = uuid4()
    response = await client.post(
        f"/api/matches/{random_match_id}/explanation/follow-up",
        json={"question": "¿Por qué el modelo le da tanta probabilidad al empate?"},
    )

    assert response.status_code == 404
