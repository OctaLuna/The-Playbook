"""Acceptance scenarios T019-T021b for explanation and follow-up endpoints."""

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

pytestmark = pytest.mark.integration


async def _fake_embedding(_: str) -> list[float]:
    return [0.01] * 1024


def _mock_cache(monkeypatch, service) -> None:
    async def no_cached_text(*_) -> None:
        return None

    async def no_cache_write(*_) -> None:
        return None

    monkeypatch.setattr(service, "get_cached_explanation", no_cached_text)
    monkeypatch.setattr(service, "cache_explanation", no_cache_write)


async def _crear_partido_con_prediccion(session: AsyncSession):
    suffix = uuid4().hex
    local = Equipo(nombre=f"Local-{suffix}", liga=Liga.PREMIER_LEAGUE)
    visitante = Equipo(nombre=f"Visitante-{suffix}", liga=Liga.PREMIER_LEAGUE)
    session.add_all([local, visitante])
    await session.flush()
    match = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        fecha_kickoff=datetime.now(UTC) + timedelta(days=2),
        estado=EstadoPartido.PROGRAMADO,
    )
    session.add(match)
    await session.flush()
    prediction = Predicción(
        partido_id=match.id,
        prob_local=0.48,
        prob_empate=0.27,
        prob_visitante=0.25,
        prob_over_2_5=0.58,
        prob_btts_si=0.55,
        xg_local=1.62,
        xg_visitante=1.11,
        nivel_confianza=NivelConfianza.MEDIA,
        head_to_head_disponible=False,
        top_shap_features={"forma_local": 0.21},
        version_modelo="test-model-v1",
        generado_en=datetime.now(UTC),
    )
    session.add(prediction)
    await session.flush()
    return match, prediction


async def test_explanation_cites_pre_kickoff_evidence_and_shap(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    _mock_cache(monkeypatch, explanations_service)
    match, _ = await _crear_partido_con_prediccion(db_session)
    evidence = Evidencia(
        url=f"https://news.example/{uuid4()}",
        titulo="El local ganó cuatro de sus últimos cinco partidos",
        texto_sanitizado="El equipo local llega con cuatro victorias recientes.",
        fecha_publicacion=match.fecha_kickoff - timedelta(days=1),
        embedding=[0.01] * 1024,
        fuente="News test",
        equipo_relacionado_id=match.equipo_local_id,
        partido_relacionado_id=match.id,
    )
    db_session.add(evidence)
    await db_session.flush()

    async def fake_generation(prompt: str) -> str:
        assert evidence.titulo in prompt
        assert "forma_local" in prompt
        return "La visita ganará seguro con una probabilidad del 90%."

    monkeypatch.setattr(explanations_service, "generar_texto", fake_generation)
    monkeypatch.setattr(explanations_service, "generar_embedding", _fake_embedding)
    response = await client.get(f"/api/matches/{match.id}/explanation")

    assert response.status_code == 200
    body = response.json()
    assert "forma_local" in body["text"]
    assert "90%" not in body["text"]
    assert body["is_fallback_no_evidence"] is False
    assert body["evidence"][0]["id"] == str(evidence.id)
    assert body["evidence"][0]["title"] == evidence.titulo
    assert body["evidence"][0]["url"] == evidence.url
    assert datetime.fromisoformat(body["evidence"][0]["published_at"]) < match.fecha_kickoff


async def test_explanation_without_evidence_returns_explicit_fallback(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    _mock_cache(monkeypatch, explanations_service)
    match, _ = await _crear_partido_con_prediccion(db_session)
    monkeypatch.setattr(
        explanations_service,
        "generar_texto",
        lambda prompt: pytest.fail("Bedrock must not run without evidence"),
    )
    monkeypatch.setattr(explanations_service, "generar_embedding", _fake_embedding)

    response = await client.get(f"/api/matches/{match.id}/explanation")

    assert response.status_code == 200
    assert response.json()["is_fallback_no_evidence"] is True
    assert response.json()["evidence"] == []
    assert "evidencia" in response.json()["text"].lower()


async def test_follow_up_reuses_original_evidence_and_does_not_predict_again(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    match, prediction = await _crear_partido_con_prediccion(db_session)
    evidence = Evidencia(
        url=f"https://news.example/{uuid4()}",
        titulo="Titular original",
        texto_sanitizado="Contexto de forma del equipo local.",
        fecha_publicacion=match.fecha_kickoff - timedelta(hours=8),
        embedding=[0.02] * 1024,
        fuente="News test",
    )
    explanation = Explicacion(
        prediccion_id=prediction.id,
        texto="El modelo favorece levemente al local por forma_local.",
        es_fallback_sin_evidencia=False,
        shap_features_usadas={"forma_local": 0.21},
    )
    db_session.add_all([evidence, explanation])
    await db_session.flush()
    db_session.add(
        ExplicacionEvidencia(
            explicacion_id=explanation.id, evidencia_id=evidence.id, orden=0
        )
    )
    await db_session.flush()

    async def fake_generation(prompt: str) -> str:
        assert "Titular original" in prompt
        assert "forma_local" in prompt
        assert "probabilities_1x2" in prompt or "0.48" in prompt
        return (
            "La señal forma_local representa el historial reciente; "
            "la probabilidad local original sigue siendo 48%."
        )

    monkeypatch.setattr(explanations_service, "generar_texto", fake_generation)
    response = await client.post(
        f"/api/matches/{match.id}/explanation/follow-up",
        json={"question": "¿Qué significa la forma reciente?"},
    )

    assert response.status_code == 200
    assert response.json()["evidence"][0]["id"] == str(evidence.id)
    assert "48%" in response.json()["answer"]


async def test_follow_up_rejects_claim_that_contradicts_prediction(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    from app.services import explanations_service

    match, prediction = await _crear_partido_con_prediccion(db_session)
    evidence = Evidencia(
        url=f"https://news.example/{uuid4()}",
        titulo="Titular original",
        texto_sanitizado="Contexto previo al partido.",
        fecha_publicacion=match.fecha_kickoff - timedelta(hours=8),
        embedding=[0.02] * 1024,
        fuente="News test",
    )
    explanation = Explicacion(
        prediccion_id=prediction.id,
        texto="La probabilidad local es 48%.",
        es_fallback_sin_evidencia=False,
        shap_features_usadas={"forma_local": 0.21},
    )
    db_session.add_all([evidence, explanation])
    await db_session.flush()
    db_session.add(
        ExplicacionEvidencia(
            explicacion_id=explanation.id, evidencia_id=evidence.id, orden=0
        )
    )
    await db_session.flush()
    async def fake_generation(_: str) -> str:
        return "La visita ganará seguro con una probabilidad del 90%."

    monkeypatch.setattr(explanations_service, "generar_texto", fake_generation)

    response = await client.post(
        f"/api/matches/{match.id}/explanation/follow-up",
        json={"question": "¿Quién ganará?"},
    )

    assert response.status_code == 200
    assert "90%" not in response.json()["answer"]
    assert "no puedo" in response.json()["answer"].lower()
