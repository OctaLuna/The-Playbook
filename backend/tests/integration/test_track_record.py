"""Pruebas de integración del Track Record Público (Grupo 4).

specs/003-track-record-publico/tasks.md.

Cubre:
- T013: Agregado con los 3 mercados (1X2, O/U 2.5, BTTS) y sus métricas [RF-001, RF-002]
- T013b: Aciertos de O/U y BTTS en casos positivos y negativos [RF-001]
- T014: Actualización por job tras nuevo partido jugado [RF-008]
- T015: Detalle partido a partido con 3 predicciones y resultado real [RF-003]
- T016: Comparación de log-loss de mercado exclusiva en 1X2 [RF-004]
- T017: Partido pospuesto excluido hasta pasar a jugado [RF-011]
- T017b: Reentrenamiento a mitad de ventana conserva versiones separadas [RF-003, RF-010]
- T018: Partido sin cuota cuenta para aciertos pero no para baseline de mercado [RF-004]
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cuota_mercado import CuotaMercado, FuenteCuota
from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import NivelConfianza, Predicción
from app.services import track_record_service
from workers.tasks.update_track_record import actualizar_track_record_job

pytestmark = pytest.mark.integration


async def _crear_partido_con_prediccion(
    session: AsyncSession,
    *,
    liga: Liga = Liga.PREMIER_LEAGUE,
    estado: EstadoPartido = EstadoPartido.JUGADO,
    goles_local: int = 2,
    goles_visitante: int = 1,
    prob_local: float = 0.50,
    prob_empate: float = 0.30,
    prob_visitante: float = 0.20,
    prob_over_2_5: float = 0.65,
    prob_btts_si: float = 0.60,
    version_modelo: str = "xgb-ensemble-2026.08.1",
    con_cuota: bool = True,
    fuente_cuota: FuenteCuota = FuenteCuota.FOOTBALL_DATA,
    kickoff: datetime | None = None,
) -> tuple[Partido, Predicción, CuotaMercado | None]:
    suffix = uuid4().hex[:8]
    local = Equipo(nombre=f"TeamA-{suffix}", liga=liga, tiene_historial_suficiente=True)
    visitante = Equipo(nombre=f"TeamB-{suffix}", liga=liga, tiene_historial_suficiente=True)
    session.add_all([local, visitante])
    await session.flush()

    partido = Partido(
        liga=liga,
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        fecha_kickoff=kickoff or (datetime.now(UTC) - timedelta(days=2)),
        estado=estado,
        goles_local=goles_local if estado == EstadoPartido.JUGADO else None,
        goles_visitante=goles_visitante if estado == EstadoPartido.JUGADO else None,
    )
    session.add(partido)
    await session.flush()

    prediccion = Predicción(
        partido_id=partido.id,
        prob_local=prob_local,
        prob_empate=prob_empate,
        prob_visitante=prob_visitante,
        prob_over_2_5=prob_over_2_5,
        prob_btts_si=prob_btts_si,
        xg_local=1.8,
        xg_visitante=1.1,
        nivel_confianza=NivelConfianza.ALTA,
        head_to_head_disponible=True,
        top_shap_features={"form": 0.3},
        version_modelo=version_modelo,
        generado_en=datetime.now(UTC) - timedelta(days=3),
    )
    session.add(prediccion)
    await session.flush()

    cuota = None
    if con_cuota:
        cuota = CuotaMercado(
            partido_id=partido.id,
            prob_implicita_local=0.52,
            prob_implicita_empate=0.28,
            prob_implicita_visitante=0.20,
            fuente=fuente_cuota,
        )
        session.add(cuota)
        await session.flush()

    return partido, prediccion, cuota


async def test_t013_agregado_devuelve_tres_mercados_con_metricas(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T013 (Historia 1, escenario 1): el agregado devuelve los tres mercados con sus métricas."""
    await _crear_partido_con_prediccion(db_session, goles_local=2, goles_visitante=1)
    await _crear_partido_con_prediccion(db_session, goles_local=0, goles_visitante=0)

    await track_record_service.evaluar_partidos_pendientes(db_session)
    await track_record_service.recalcular_track_record_agregado(db_session, ventana_n=50)

    res = await client.get("/api/track-record")
    assert res.status_code == 200
    data = res.json()

    assert data["window_size"] == 50
    assert data["matches_included"] == 2
    assert len(data["markets"]) == 3

    mercados = {m["market"]: m for m in data["markets"]}
    assert "1x2" in mercados
    assert "over_under_2_5" in mercados
    assert "btts" in mercados

    for m in mercados.values():
        assert 0.0 <= m["hit_rate"] <= 1.0
        assert m["avg_brier_score"] >= 0.0
        assert m["avg_log_loss"] >= 0.0


async def test_t013b_acierto_over_under_y_btts_ambos_signos(db_session: AsyncSession) -> None:
    """T013b: evaluación correcta de acierto y desacierto en Over/Under y BTTS."""
    # Caso 1: Over acertado (3 goles, pred>0.5), BTTS acertado (ambos anotan, pred>0.5)
    p1, pred1, _ = await _crear_partido_con_prediccion(
        db_session,
        goles_local=2,
        goles_visitante=1,
        prob_over_2_5=0.8,
        prob_btts_si=0.7,
    )
    ev1 = track_record_service.evaluar_partido(p1, pred1)
    assert ev1.acierto_over_under_2_5 is True
    assert ev1.acierto_btts is True

    # Caso 2: Over fallado (1 gol, pred>0.5 predice over),
    # BTTS fallado (1 equipo anota, pred>0.5 predice sí)
    p2, pred2, _ = await _crear_partido_con_prediccion(
        db_session,
        goles_local=1,
        goles_visitante=0,
        prob_over_2_5=0.8,
        prob_btts_si=0.7,
    )
    ev2 = track_record_service.evaluar_partido(p2, pred2)
    assert ev2.acierto_over_under_2_5 is False
    assert ev2.acierto_btts is False

    # Caso 3: Under acertado (1 gol, pred<0.5 predice under), No-BTTS acertado (pred<0.5 predice no)
    p3, pred3, _ = await _crear_partido_con_prediccion(
        db_session,
        goles_local=1,
        goles_visitante=0,
        prob_over_2_5=0.2,
        prob_btts_si=0.3,
    )
    ev3 = track_record_service.evaluar_partido(p3, pred3)
    assert ev3.acierto_over_under_2_5 is True
    assert ev3.acierto_btts is True


async def test_t014_job_actualiza_track_record_tras_nuevo_partido_jugado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T014 (Historia 1, escenario 2): job Celery incorpora nuevos partidos jugados."""
    await _crear_partido_con_prediccion(db_session, goles_local=1, goles_visitante=0)
    await actualizar_track_record_job(db_session, ventana_n=50)

    res1 = await client.get("/api/track-record")
    assert res1.json()["matches_included"] == 1

    # Agregamos segundo partido
    await _crear_partido_con_prediccion(db_session, goles_local=2, goles_visitante=2)
    await actualizar_track_record_job(db_session, ventana_n=50)

    res2 = await client.get("/api/track-record")
    assert res2.json()["matches_included"] == 2


async def test_t015_detalle_partido_a_partido_con_tres_predicciones_y_resultado_real(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T015 (Historia 2): detalle partido a partido con las 3 predicciones y resultado real."""
    partido, _, _ = await _crear_partido_con_prediccion(
        db_session, goles_local=3, goles_visitante=1
    )
    await actualizar_track_record_job(db_session)

    res = await client.get("/api/track-record/matches")
    assert res.status_code == 200
    data = res.json()

    assert data["total"] >= 1
    item = next(m for m in data["matches"] if m["match_id"] == str(partido.id))

    assert item["real_result"] == {"home_goals": 3, "away_goals": 1}
    assert "predicted_1x2" in item
    assert "predicted_over_under_2_5" in item
    assert "predicted_btts" in item
    assert item["hit_1x2"] is True
    assert item["hit_over_under_2_5"] is True
    assert item["hit_btts"] is True
    assert item["has_market_odds"] is True
    assert item["market_implied_1x2"] is not None
    assert item["model_version"] == "xgb-ensemble-2026.08.1"


async def test_t016_avg_market_log_loss_solo_en_1x2_y_comparable(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T016 (Historia 3): avg_market_log_loss solo está presente en 1x2, nulo en O/U y BTTS."""
    await _crear_partido_con_prediccion(db_session, con_cuota=True)
    await actualizar_track_record_job(db_session)

    res = await client.get("/api/track-record")
    data = res.json()
    mercados = {m["market"]: m for m in data["markets"]}

    m_1x2 = mercados["1x2"]
    assert m_1x2["avg_market_log_loss"] is not None
    assert m_1x2["avg_market_log_loss"] > 0
    assert m_1x2["market_baseline_matches"] >= 1

    assert mercados["over_under_2_5"]["avg_market_log_loss"] is None
    assert mercados["over_under_2_5"]["market_baseline_matches"] == 0
    assert mercados["btts"]["avg_market_log_loss"] is None
    assert mercados["btts"]["market_baseline_matches"] == 0


async def test_t017_partido_pospuesto_se_excluye_hasta_que_pasa_a_jugado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T017: partidos pospuestos no se evalúan ni se incluyen en agregados."""
    p_pospuesto, _, _ = await _crear_partido_con_prediccion(
        db_session, estado=EstadoPartido.POSPUESTO
    )
    await _crear_partido_con_prediccion(db_session, estado=EstadoPartido.JUGADO)

    await actualizar_track_record_job(db_session)

    res = await client.get("/api/track-record")
    assert res.json()["matches_included"] == 1

    # Cuando pasa a jugado, se incorpora
    p_pospuesto.estado = EstadoPartido.JUGADO
    p_pospuesto.goles_local = 1
    p_pospuesto.goles_visitante = 1
    await db_session.flush()

    await actualizar_track_record_job(db_session)

    res2 = await client.get("/api/track-record")
    assert res2.json()["matches_included"] == 2


async def test_t017b_reentrenamiento_mitad_ventana_dos_versiones_modelo(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T017b: reentrenamiento a mitad de ventana expone ambas versiones sin mezclarlas."""
    now = datetime.now(UTC)
    await _crear_partido_con_prediccion(
        db_session,
        version_modelo="xgb-v1.0",
        kickoff=now - timedelta(days=5),
    )
    await _crear_partido_con_prediccion(
        db_session,
        version_modelo="xgb-v2.0",
        kickoff=now - timedelta(days=2),
    )
    await actualizar_track_record_job(db_session)

    # El agregado lista ambas versiones
    res_agg = await client.get("/api/track-record")
    versiones = res_agg.json()["model_versions"]
    assert "xgb-v1.0" in versiones
    assert "xgb-v2.0" in versiones

    # El detalle conserva la versión específica de cada partido
    res_matches = await client.get("/api/track-record/matches")
    items = res_matches.json()["matches"]
    versiones_partidos = {item["model_version"] for item in items}
    assert "xgb-v1.0" in versiones_partidos
    assert "xgb-v2.0" in versiones_partidos


async def test_t018_partido_sin_cuota_cuenta_para_hit_rate_pero_no_para_baseline(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """T018: partido sin CuotaMercado cuenta para hit_rate pero no para baseline de mercado."""
    await _crear_partido_con_prediccion(db_session, con_cuota=True)
    await _crear_partido_con_prediccion(db_session, con_cuota=False)
    await actualizar_track_record_job(db_session)

    res = await client.get("/api/track-record")
    data = res.json()

    assert data["matches_included"] == 2
    m_1x2 = next(m for m in data["markets"] if m["market"] == "1x2")
    # Solo 1 partido tenía cuota de mercado
    assert m_1x2["market_baseline_matches"] == 1
    assert m_1x2["avg_market_log_loss"] is not None
