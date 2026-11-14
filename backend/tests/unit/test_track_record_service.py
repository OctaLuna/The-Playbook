"""Pruebas unitarias de track_record_service (Grupo 3 de specs/003-track-record-publico/tasks.md).

Cubre:
- T009: Evaluación de los 3 mercados con métricas de ml.evaluation (brier, log-loss)
- T010: Precedencia de fuentes de cuotas y cálculo de log_loss_mercado_1x2
- Determinación de aciertos 1X2, Over/Under 2.5 y BTTS
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models.cuota_mercado import CuotaMercado, FuenteCuota
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import NivelConfianza, Predicción
from app.services.track_record_service import (
    determinar_acierto_1x2,
    determinar_acierto_btts,
    determinar_acierto_over_under_2_5,
    determinar_resultado_real_1x2,
    evaluar_partido,
    seleccionar_cuota_mercado,
)

pytestmark = pytest.mark.unit


def test_determinar_resultado_real_1x2() -> None:
    assert determinar_resultado_real_1x2(2, 1) == "local"
    assert determinar_resultado_real_1x2(1, 1) == "empate"
    assert determinar_resultado_real_1x2(0, 3) == "visitante"


def test_determinar_acierto_1x2() -> None:
    # Máxima probabilidad: local (0.6)
    assert determinar_acierto_1x2(0.6, 0.25, 0.15, "local") is True
    assert determinar_acierto_1x2(0.6, 0.25, 0.15, "empate") is False

    # Máxima probabilidad: empate (0.5)
    assert determinar_acierto_1x2(0.2, 0.5, 0.3, "empate") is True
    assert determinar_acierto_1x2(0.2, 0.5, 0.3, "visitante") is False

    # Máxima probabilidad: visitante (0.7)
    assert determinar_acierto_1x2(0.1, 0.2, 0.7, "visitante") is True


def test_determinar_acierto_over_under_2_5() -> None:
    # Over 2.5 real (3 goles)
    assert determinar_acierto_over_under_2_5(0.7, 2, 1) is True  # Predice over (>=0.5) -> Acierto
    assert determinar_acierto_over_under_2_5(0.3, 2, 1) is False  # Predice under (<0.5) -> Fallo

    # Under 2.5 real (1 gol)
    assert determinar_acierto_over_under_2_5(0.7, 1, 0) is False  # Predice over -> Fallo
    assert determinar_acierto_over_under_2_5(0.3, 1, 0) is True  # Predice under -> Acierto


def test_determinar_acierto_btts() -> None:
    # Ambos anotan (2-1)
    assert determinar_acierto_btts(0.6, 2, 1) is True  # Predice sí -> Acierto
    assert determinar_acierto_btts(0.4, 2, 1) is False  # Predice no -> Fallo

    # Solo uno anota (2-0)
    assert determinar_acierto_btts(0.6, 2, 0) is False  # Predice sí -> Fallo
    assert determinar_acierto_btts(0.4, 2, 0) is True  # Predice no -> Acierto


def test_seleccionar_cuota_mercado_precedencia() -> None:
    pid = uuid4()
    c_kaggle = CuotaMercado(
        partido_id=pid,
        prob_implicita_local=0.5,
        prob_implicita_empate=0.3,
        prob_implicita_visitante=0.2,
        fuente=FuenteCuota.KAGGLE,
    )
    c_operativa = CuotaMercado(
        partido_id=pid,
        prob_implicita_local=0.55,
        prob_implicita_empate=0.25,
        prob_implicita_visitante=0.20,
        fuente=FuenteCuota.OPERATIVA,
    )
    c_football_data = CuotaMercado(
        partido_id=pid,
        prob_implicita_local=0.48,
        prob_implicita_empate=0.32,
        prob_implicita_visitante=0.20,
        fuente=FuenteCuota.FOOTBALL_DATA,
    )

    # Si están las 3, gana football_data
    assert seleccionar_cuota_mercado([c_operativa, c_kaggle, c_football_data]) == c_football_data

    # Si no está football_data, gana kaggle sobre operativa
    assert seleccionar_cuota_mercado([c_operativa, c_kaggle]) == c_kaggle

    # Si solo está operativa, se usa operativa
    assert seleccionar_cuota_mercado([c_operativa]) == c_operativa

    # Si lista vacía, None
    assert seleccionar_cuota_mercado([]) is None


def test_evaluar_partido_con_y_sin_cuota() -> None:
    pid = uuid4()
    partido = Partido(
        id=pid,
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=uuid4(),
        equipo_visitante_id=uuid4(),
        fecha_kickoff=datetime.now(UTC),
        estado=EstadoPartido.JUGADO,
        goles_local=2,
        goles_visitante=1,
    )
    prediccion = Predicción(
        id=uuid4(),
        partido_id=pid,
        prob_local=0.60,
        prob_empate=0.25,
        prob_visitante=0.15,
        prob_over_2_5=0.70,
        prob_btts_si=0.65,
        xg_local=2.0,
        xg_visitante=1.0,
        nivel_confianza=NivelConfianza.ALTA,
        head_to_head_disponible=True,
        top_shap_features={},
        version_modelo="xgb-v1",
        generado_en=datetime.now(UTC),
    )

    # 1. Sin cuota
    ev_sin_cuota = evaluar_partido(partido, prediccion, cuotas=[])
    assert ev_sin_cuota.acierto_1x2 is True
    assert ev_sin_cuota.acierto_over_under_2_5 is True
    assert ev_sin_cuota.acierto_btts is True
    assert ev_sin_cuota.tiene_cuota_mercado is False
    assert ev_sin_cuota.log_loss_mercado_1x2 is None
    assert ev_sin_cuota.brier_1x2 > 0
    assert ev_sin_cuota.log_loss_1x2 > 0
    assert ev_sin_cuota.brier_over_under_2_5 > 0
    assert ev_sin_cuota.brier_btts > 0
    assert ev_sin_cuota.version_modelo == "xgb-v1"

    # 2. Con cuota
    cuota = CuotaMercado(
        partido_id=pid,
        prob_implicita_local=0.55,
        prob_implicita_empate=0.25,
        prob_implicita_visitante=0.20,
        fuente=FuenteCuota.FOOTBALL_DATA,
    )
    ev_con_cuota = evaluar_partido(partido, prediccion, cuotas=[cuota])
    assert ev_con_cuota.tiene_cuota_mercado is True
    assert ev_con_cuota.log_loss_mercado_1x2 is not None
    assert ev_con_cuota.log_loss_mercado_1x2 > 0
