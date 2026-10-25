"""Pruebas de contrato de la API de explicaciones (T002, T003).

Endpoints:
- GET /api/matches/{match_id}/explanation (incluye 404)
- POST /api/matches/{match_id}/explanation/follow-up (incluye 404)
Cumple con contracts/explanations-api.md.
"""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.models.evidencia import Evidencia
from app.models.explicacion import Explicacion
from app.models.explicacion_evidencia import ExplicacionEvidencia


@pytest.mark.asyncio
async def test_get_explanation_returns_404_when_not_found(client: AsyncClient) -> None:
    non_existent_match_id = uuid.uuid4()
    response = await client.get(f"/api/matches/{non_existent_match_id}/explanation")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_explanation_success_contract(client: AsyncClient, db_session) -> None:
    match_id = uuid.uuid4()
    prediccion_id = match_id  # o id de prediccion asociada

    evidencia = Evidencia(
        id=uuid.uuid4(),
        url="https://ejemplo.com/noticia-prueba",
        titulo="El delantero estrella es baja de ltima hora",
        texto_sanitizado="Noticia deportiva sanitizada.",
        fecha_publicacion=datetime(2026, 8, 27, 10, 0, 0, tzinfo=UTC),
        fuente="News API",
        embedding=[0.0] * 1024,
    )
    db_session.add(evidencia)
    await db_session.flush()

    explicacion = Explicacion(
        id=uuid.uuid4(),
        match_id=match_id,
        prediccion_id=prediccion_id,
        texto=(
            "El modelo favorece al local debido a su forma reciente "
            "y la ausencia del delantero rival."
        ),
        es_fallback_sin_evidencia=False,
        shap_features_usadas={"forma_reciente": 0.35, "lesion_delantero": 0.22},
        generado_en=datetime(2026, 8, 29, 6, 5, 0, tzinfo=UTC),
        actualizado_en=datetime(2026, 8, 29, 6, 5, 0, tzinfo=UTC),
    )
    db_session.add(explicacion)
    await db_session.flush()

    puente = ExplicacionEvidencia(
        explicacion_id=explicacion.id,
        evidencia_id=evidencia.id,
        orden=1,
    )
    db_session.add(puente)
    await db_session.commit()

    response = await client.get(f"/api/matches/{match_id}/explanation")
    assert response.status_code == 200

    data = response.json()
    assert data["match_id"] == str(match_id)
    assert isinstance(data["text"], str)
    assert data["is_fallback_no_evidence"] is False
    assert isinstance(data["evidence"], list)
    assert len(data["evidence"]) >= 1

    ev_item = data["evidence"][0]
    assert ev_item["id"] == str(evidencia.id)
    assert ev_item["title"] == evidencia.titulo
    assert ev_item["url"] == evidencia.url
    assert ev_item["source"] == evidencia.fuente
    assert "published_at" in ev_item
    assert "generated_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_post_follow_up_returns_404_when_no_prior_explanation(client: AsyncClient) -> None:
    non_existent_match_id = uuid.uuid4()
    response = await client.post(
        f"/api/matches/{non_existent_match_id}/explanation/follow-up",
        json={"question": "Por qu pesa tanto la lesin?"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_follow_up_success_contract(client: AsyncClient, db_session) -> None:
    match_id = uuid.uuid4()
    prediccion_id = match_id

    explicacion = Explicacion(
        id=uuid.uuid4(),
        match_id=match_id,
        prediccion_id=prediccion_id,
        texto="Explicacin base para el partido.",
        es_fallback_sin_evidencia=False,
        shap_features_usadas={"forma_reciente": 0.35},
        generado_en=datetime(2026, 8, 29, 6, 5, 0, tzinfo=UTC),
        actualizado_en=datetime(2026, 8, 29, 6, 5, 0, tzinfo=UTC),
    )
    db_session.add(explicacion)
    await db_session.commit()

    response = await client.post(
        f"/api/matches/{match_id}/explanation/follow-up",
        json={"question": "Por qu pesa tanto la forma reciente?"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["match_id"] == str(match_id)
    assert data["question"] == "Por qu pesa tanto la forma reciente?"
    assert isinstance(data["answer"], str)
    assert isinstance(data["evidence"], list)
    assert "generated_at" in data
