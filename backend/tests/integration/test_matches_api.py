"""Integración de las cuatro señales de 001 contra PostgreSQL real."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calibracion_historica import CalibraciónHistórica, Mercado
from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import NivelConfianza, Predicción

pytestmark = pytest.mark.integration


async def _crear_partido(
    session: AsyncSession,
    *,
    kickoff: datetime | None = None,
    estado: EstadoPartido = EstadoPartido.PROGRAMADO,
    historial_local: bool = True,
    historial_visitante: bool = True,
    head_to_head: bool = True,
    con_prediccion: bool = True,
) -> tuple[UUID, UUID | None]:
    suffix = uuid4().hex[:8]
    local = Equipo(
        nombre=f"Arsenal-{suffix}",
        liga=Liga.PREMIER_LEAGUE,
        tiene_historial_suficiente=historial_local,
    )
    visitante = Equipo(
        nombre=f"Chelsea-{suffix}",
        liga=Liga.PREMIER_LEAGUE,
        tiene_historial_suficiente=historial_visitante,
    )
    session.add_all([local, visitante])
    await session.flush()

    partido = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        fecha_kickoff=kickoff or datetime.now(UTC) + timedelta(hours=8),
        estado=estado,
        goles_local=2 if estado == EstadoPartido.JUGADO else None,
        goles_visitante=1 if estado == EstadoPartido.JUGADO else None,
    )
    session.add(partido)
    await session.flush()

    prediccion_id = None
    if con_prediccion:
        prediccion = Predicción(
            partido_id=partido.id,
            prob_local=0.48,
            prob_empate=0.27,
            prob_visitante=0.25,
            prob_over_2_5=0.58,
            prob_btts_si=0.55,
            xg_local=1.62,
            xg_visitante=1.11,
            nivel_confianza=NivelConfianza.MEDIA,
            head_to_head_disponible=head_to_head,
            top_shap_features={"forma_local": 0.21},
            version_modelo="test-model-v1",
            generado_en=datetime.now(UTC),
        )
        session.add(prediccion)
        await session.flush()
        prediccion_id = prediccion.id
    return partido.id, prediccion_id


async def test_prediction_entrega_las_cuatro_senales_y_1x2_suma_uno(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session)
    db_session.add(
        CalibraciónHistórica(
            mercado=Mercado.UNO_X_DOS,
            rango_probabilidad_min=0.4,
            rango_probabilidad_max=0.5,
            precision_empirica=0.8,
            n_observaciones=30,
            version_modelo="test-model-v1",
        )
    )
    await db_session.flush()

    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 200
    body = response.json()
    assert sum(body["probabilities_1x2"].values()) == pytest.approx(1.0)
    assert body["over_under_2_5"]["over"] == pytest.approx(0.58)
    assert body["over_under_2_5"]["under"] == pytest.approx(0.42)
    assert body["btts"]["yes"] == pytest.approx(0.55)
    assert body["btts"]["no"] == pytest.approx(0.45)
    assert body["xg"] == {"home": 1.62, "away": 1.11}
    assert body["confidence"] == "alta"
    assert "top_shap_features" not in body


async def test_prediction_avisa_si_falta_historial_de_un_equipo(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session, historial_local=False)

    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 200
    assert response.json()["low_data_warning"] is True


async def test_prediction_devuelve_confianza_baja_sin_calibracion_suficiente(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session)

    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 200
    assert response.json()["confidence"] == "baja"


async def test_partido_pospuesto_conserva_prediccion_original(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session, estado=EstadoPartido.POSPUESTO)

    detalle = await client.get(f"/api/matches/{match_id}")
    prediccion = await client.get(f"/api/matches/{match_id}/prediction")

    assert detalle.status_code == 200
    assert detalle.json()["status"] == "postponed"
    assert prediccion.status_code == 200
    assert prediccion.json()["probabilities_1x2"] == {
        "home": 0.48,
        "draw": 0.27,
        "away": 0.25,
    }


async def test_prediction_sin_head_to_head_devuelve_false(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session, head_to_head=False)

    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 200
    assert response.json()["head_to_head_available"] is False


async def test_partido_sin_prediccion_devuelve_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    match_id, _ = await _crear_partido(db_session, con_prediccion=False)

    response = await client.get(f"/api/matches/{match_id}/prediction")

    assert response.status_code == 404


async def test_upcoming_pagina_y_expone_si_hay_prediccion(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inicio = datetime.now(UTC)
    await _crear_partido(
        db_session,
        kickoff=inicio + timedelta(hours=3),
        con_prediccion=True,
    )
    await _crear_partido(
        db_session,
        kickoff=inicio + timedelta(hours=5),
        con_prediccion=False,
    )

    response = await client.get(
        "/api/matches/upcoming",
        params={
            "league": "premier_league",
            "from": inicio.isoformat(),
            "to": (inicio + timedelta(days=1)).isoformat(),
            "page": 1,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 1
    assert body["matches"][0]["has_prediction"] is True
