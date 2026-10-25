"""
Contrato de la API de Explicaciones en Lenguaje Natural (002-explicacion-lenguaje-natural).

Grupo 1 de `specs/002-explicacion-lenguaje-natural/tasks.md` (T002, T003)
— fase Red del Artículo III:
Verifica el cumplimiento del contrato definido en `contracts/explanations-api.md`.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipo import Equipo
from app.models.evidencia import Evidencia
from app.models.explicacion import Explicacion
from app.models.explicacion_evidencia import ExplicacionEvidencia
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import NivelConfianza, Predicción

pytestmark = pytest.mark.contract


async def _match_with_prediction(session: AsyncSession):
    suffix = uuid4().hex
    home = Equipo(nombre=f"Home-{suffix}", liga=Liga.PREMIER_LEAGUE)
    away = Equipo(nombre=f"Away-{suffix}", liga=Liga.PREMIER_LEAGUE)
    session.add_all([home, away])
    await session.flush()
    match = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=home.id,
        equipo_visitante_id=away.id,
        fecha_kickoff=datetime.now(UTC) + timedelta(days=2),
        estado=EstadoPartido.PROGRAMADO,
    )
    session.add(match)
    await session.flush()
    prediction = Predicción(
        partido_id=match.id,
        prob_local=0.5,
        prob_empate=0.25,
        prob_visitante=0.25,
        prob_over_2_5=0.5,
        prob_btts_si=0.5,
        xg_local=1.4,
        xg_visitante=1.0,
        nivel_confianza=NivelConfianza.MEDIA,
        head_to_head_disponible=False,
        top_shap_features={"forma_local": 0.2},
        version_modelo="contract-test",
        generado_en=datetime.now(UTC),
    )
    session.add(prediction)
    await session.flush()
    return match, prediction


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


async def test_get_explanation_success_contract(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    match, _ = await _match_with_prediction(db_session)
    evidence = Evidencia(
        url=f"https://news.example/{uuid4()}",
        titulo="Forma reciente",
        texto_sanitizado="El equipo llega en buena forma.",
        fecha_publicacion=match.fecha_kickoff - timedelta(days=1),
        embedding=[0.01] * 1024,
        fuente="Contract test",
    )
    db_session.add(evidence)
    await db_session.flush()

    async def fake_embedding(_: str) -> list[float]:
        return [0.01] * 1024

    async def fake_generation(_: str) -> str:
        return "La forma reciente favorece al equipo local."

    async def no_cache(*_) -> None:
        return None

    monkeypatch.setattr(explanations_service, "generar_embedding", fake_embedding)
    monkeypatch.setattr(explanations_service, "generar_texto", fake_generation)
    monkeypatch.setattr(explanations_service, "get_cached_explanation", no_cache)
    monkeypatch.setattr(explanations_service, "cache_explanation", no_cache)

    response = await client.get(f"/api/matches/{match.id}/explanation")
    assert response.status_code == 200
    body = response.json()
    assert body["match_id"] == str(match.id)
    assert body["is_fallback_no_evidence"] is False
    assert body["evidence"][0]["url"] == evidence.url
    assert body["evidence"][0]["title"] == evidence.titulo


async def test_follow_up_success_contract(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    match, prediction = await _match_with_prediction(db_session)
    evidence = Evidencia(
        url=f"https://news.example/{uuid4()}",
        titulo="Forma reciente",
        texto_sanitizado="El equipo llega en buena forma.",
        fecha_publicacion=match.fecha_kickoff - timedelta(days=1),
        embedding=[0.01] * 1024,
        fuente="Contract test",
    )
    explanation = Explicacion(
        prediccion_id=prediction.id,
        texto="La forma reciente es favorable.",
        es_fallback_sin_evidencia=False,
        shap_features_usadas={"forma_local": 0.2},
    )
    db_session.add_all([evidence, explanation])
    await db_session.flush()
    db_session.add(
        ExplicacionEvidencia(explicacion_id=explanation.id, evidencia_id=evidence.id, orden=0)
    )
    await db_session.flush()

    async def fake_generation(_: str) -> str:
        return "La señal forma_local resume los resultados recientes."

    monkeypatch.setattr(explanations_service, "generar_texto", fake_generation)
    response = await client.post(
        f"/api/matches/{match.id}/explanation/follow-up",
        json={"question": "¿Qué significa forma local?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["match_id"] == str(match.id)
    assert body["question"] == "¿Qué significa forma local?"
    assert body["answer"]
    assert body["evidence"][0]["url"] == evidence.url
