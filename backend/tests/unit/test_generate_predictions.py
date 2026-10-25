"""Unit and integration boundaries for Celery prediction generation (001 T016)."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.models.partido import EstadoPartido, Liga, Partido
from workers.tasks.generate_predictions import dentro_ventana_prediccion


def test_prediction_window_is_open_only_during_last_24_hours() -> None:
    now = datetime(2026, 10, 25, 12, tzinfo=UTC)

    assert dentro_ventana_prediccion(now + timedelta(hours=24), now) is True
    assert dentro_ventana_prediccion(now + timedelta(hours=23, minutes=59), now) is True
    assert dentro_ventana_prediccion(now + timedelta(hours=24, seconds=1), now) is False
    assert dentro_ventana_prediccion(now - timedelta(seconds=1), now) is False


@pytest.mark.integration
async def test_worker_persists_one_prediction_for_each_eligible_match(
    db_session, monkeypatch
) -> None:
    from sqlalchemy import select

    from app.models.equipo import Equipo
    from app.models.prediccion import NivelConfianza, Predicción
    from workers.tasks import generate_predictions as task

    now = datetime.now(UTC)
    home = Equipo(nombre=f"home-{uuid4()}", liga=Liga.PREMIER_LEAGUE)
    away = Equipo(nombre=f"away-{uuid4()}", liga=Liga.PREMIER_LEAGUE)
    db_session.add_all([home, away])
    await db_session.flush()
    eligible = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=home.id,
        equipo_visitante_id=away.id,
        fecha_kickoff=now + timedelta(hours=12),
        estado=EstadoPartido.PROGRAMADO,
    )
    outside = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=home.id,
        equipo_visitante_id=away.id,
        fecha_kickoff=now + timedelta(hours=30),
        estado=EstadoPartido.PROGRAMADO,
    )
    db_session.add_all([eligible, outside])
    await db_session.flush()

    monkeypatch.setattr(
        task,
        "entrenar_y_predecir",
        lambda partidos_historicos, partidos_objetivo: {
            partido.id: {
                "prob_local": 0.5,
                "prob_empate": 0.25,
                "prob_visitante": 0.25,
                "prob_over_2_5": 0.6,
                "prob_btts_si": 0.55,
                "xg_local": 1.7,
                "xg_visitante": 1.1,
                "head_to_head_disponible": False,
                "top_shap_features": {"forma_local": 0.3},
                "version_modelo": "test-model-v1",
            }
            for partido in partidos_objetivo
        },
    )

    generated = await task.generar_predicciones_para_ventana(db_session, ahora=now)
    rows = (await db_session.execute(select(Predicción))).scalars().all()

    assert generated == 1
    assert len(rows) == 1
    assert rows[0].partido_id == eligible.id
    assert rows[0].top_shap_features == {"forma_local": 0.3}
    assert rows[0].version_modelo == "test-model-v1"
    assert rows[0].nivel_confianza == NivelConfianza.BAJA


@pytest.mark.integration
async def test_worker_does_not_overwrite_existing_prediction(db_session, monkeypatch) -> None:
    from sqlalchemy import select

    from app.models.equipo import Equipo
    from app.models.prediccion import NivelConfianza, Predicción
    from workers.tasks import generate_predictions as task

    now = datetime.now(UTC)
    home = Equipo(nombre=f"home-{uuid4()}", liga=Liga.PREMIER_LEAGUE)
    away = Equipo(nombre=f"away-{uuid4()}", liga=Liga.PREMIER_LEAGUE)
    db_session.add_all([home, away])
    await db_session.flush()
    match = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=home.id,
        equipo_visitante_id=away.id,
        fecha_kickoff=now + timedelta(hours=12),
        estado=EstadoPartido.PROGRAMADO,
    )
    db_session.add(match)
    await db_session.flush()
    original = Predicción(
        partido_id=match.id,
        prob_local=0.4,
        prob_empate=0.3,
        prob_visitante=0.3,
        prob_over_2_5=0.5,
        prob_btts_si=0.5,
        xg_local=1.2,
        xg_visitante=1.0,
        nivel_confianza=NivelConfianza.BAJA,
        head_to_head_disponible=False,
        top_shap_features={},
        version_modelo="original-v1",
        generado_en=now,
    )
    db_session.add(original)
    await db_session.flush()

    monkeypatch.setattr(task, "entrenar_y_predecir", lambda *_: pytest.fail("must not retrain"))
    generated = await task.generar_predicciones_para_ventana(db_session, ahora=now)
    rows = (await db_session.execute(select(Predicción))).scalars().all()

    assert generated == 0
    assert len(rows) == 1
    assert rows[0].version_modelo == "original-v1"
