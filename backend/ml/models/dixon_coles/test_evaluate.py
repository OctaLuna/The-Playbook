"""Contrato de `ml.models.dixon_coles.evaluate` (T012d).

Ver `ml-design.md` §7: las mismas funciones de `ml.evaluation.metrics`
(log-loss, Brier score) que reutiliza `003-track-record-publico`, aplicadas
a los tres mercados (1X2, Over/Under 2.5, BTTS) que salen de la matriz de
Dixon-Coles — nunca una fórmula propia reimplementada acá (Artículo VIII).

Fase Red (Artículo III): `ml.models.dixon_coles.evaluate` todavía no existe.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models.partido import EstadoPartido, Liga, Partido

pytestmark = pytest.mark.unit

_LOCAL = uuid4()
_VISITANTE = uuid4()
_KICKOFF = datetime(2024, 10, 1, 15, 0, tzinfo=UTC)


def _parametros_neutros():
    from ml.models.dixon_coles.train import ParametrosDixonColes

    return ParametrosDixonColes(
        alpha={_LOCAL: 0.0, _VISITANTE: 0.0},
        beta={_LOCAL: 0.0, _VISITANTE: 0.0},
        gamma=0.0,
        rho=0.0,
        xi=0.0018,
    )


def _partido(*, goles_local, goles_visitante, estado=EstadoPartido.JUGADO) -> Partido:
    return Partido(
        id=uuid4(),
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=_LOCAL,
        equipo_visitante_id=_VISITANTE,
        fecha_kickoff=_KICKOFF,
        estado=estado,
        goles_local=goles_local,
        goles_visitante=goles_visitante,
    )


def test_no_hay_partidos_jugados_falla_explicito() -> None:
    from ml.models.dixon_coles.evaluate import evaluar_dixon_coles

    solo_programado = [_partido(goles_local=0, goles_visitante=0, estado=EstadoPartido.PROGRAMADO)]

    with pytest.raises(ValueError, match="No hay partidos"):
        evaluar_dixon_coles(_parametros_neutros(), solo_programado)


def test_devuelve_log_loss_y_brier_para_los_tres_mercados() -> None:
    from ml.models.dixon_coles.evaluate import evaluar_dixon_coles

    metricas = evaluar_dixon_coles(
        _parametros_neutros(), [_partido(goles_local=2, goles_visitante=0)]
    )

    assert set(metricas) == {"1x2", "over_under_2_5", "btts"}
    for mercado in metricas.values():
        assert set(mercado) == {"log_loss", "brier"}
        assert mercado["log_loss"] >= 0.0
        assert 0.0 <= mercado["brier"] <= 2.0


def test_el_brier_de_1x2_coincide_con_ml_evaluation_metrics() -> None:
    """No reimplementa la fórmula — delega en `ml.evaluation.metrics`
    (Artículo VIII), así que el resultado agregado debe coincidir con
    llamar esas funciones a mano sobre la misma predicción."""
    from ml.evaluation.metrics import brier_score_1x2
    from ml.models.dixon_coles.evaluate import evaluar_dixon_coles
    from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, probabilidad_1x2
    from ml.models.dixon_coles.train import ParametrosDixonColes

    parametros = ParametrosDixonColes(
        alpha={_LOCAL: 0.3, _VISITANTE: -0.2},
        beta={_LOCAL: -0.1, _VISITANTE: 0.15},
        gamma=0.2,
        rho=0.03,
        xi=0.0018,
    )
    partido = _partido(goles_local=1, goles_visitante=1)

    metricas = evaluar_dixon_coles(parametros, [partido])

    from ml.models.dixon_coles.predict import tasas_esperadas

    lam_val, mu_val = tasas_esperadas(parametros, _LOCAL, _VISITANTE)
    matriz = matriz_probabilidad_marcador(lam_val, mu_val, parametros.rho)
    prob_1x2 = probabilidad_1x2(matriz)
    esperado = brier_score_1x2(prob_1x2, "empate")

    assert metricas["1x2"]["brier"] == pytest.approx(esperado)


def test_promedia_las_metricas_sobre_todos_los_partidos_de_validacion() -> None:
    from ml.models.dixon_coles.evaluate import evaluar_dixon_coles

    un_partido = [_partido(goles_local=2, goles_visitante=0)]
    dos_partidos_iguales = un_partido * 2

    metricas_uno = evaluar_dixon_coles(_parametros_neutros(), un_partido)
    metricas_dos = evaluar_dixon_coles(_parametros_neutros(), dos_partidos_iguales)

    assert metricas_uno["1x2"]["log_loss"] == pytest.approx(metricas_dos["1x2"]["log_loss"])
