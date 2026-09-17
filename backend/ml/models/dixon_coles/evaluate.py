"""Evaluación de Dixon-Coles vía log-loss/Brier (ml-design.md §7).

Reutiliza `ml.evaluation.metrics` tal cual — las mismas funciones que
`003-track-record-publico` usa para `EvaluaciónPredicción` (Artículo VIII: una
sola implementación, nunca reimplementada acá).

Ver `test_evaluate.py` para el contrato completo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.models.partido import EstadoPartido
from ml.evaluation.metrics import (
    brier_score_1x2,
    brier_score_binario,
    log_loss_1x2,
    log_loss_binario,
)
from ml.models.dixon_coles.predict import (
    matriz_probabilidad_marcador,
    probabilidad_1x2,
    probabilidad_btts,
    probabilidad_over_under_2_5,
    tasas_esperadas,
)

if TYPE_CHECKING:
    from app.models.partido import Partido
    from ml.models.dixon_coles.train import ParametrosDixonColes

MERCADOS = ("1x2", "over_under_2_5", "btts")


def _resultado_1x2(partido: Partido) -> str:
    if partido.goles_local > partido.goles_visitante:
        return "local"
    if partido.goles_local == partido.goles_visitante:
        return "empate"
    return "visitante"


def evaluar_dixon_coles(
    parametros: ParametrosDixonColes, partidos_validacion: list[Partido]
) -> dict[str, dict[str, float]]:
    """Log-loss y Brier score promedio de `parametros` sobre
    `partidos_validacion`, uno por mercado (1X2, Over/Under 2.5, BTTS)."""
    jugados = [p for p in partidos_validacion if p.estado == EstadoPartido.JUGADO]
    if not jugados:
        raise ValueError("No hay partidos jugados para evaluar Dixon-Coles.")

    acumulado = {mercado: {"log_loss": 0.0, "brier": 0.0} for mercado in MERCADOS}

    for partido in jugados:
        lam, mu = tasas_esperadas(parametros, partido.equipo_local_id, partido.equipo_visitante_id)
        matriz = matriz_probabilidad_marcador(lam, mu, parametros.rho)

        prob_1x2 = probabilidad_1x2(matriz)
        resultado_1x2 = _resultado_1x2(partido)
        acumulado["1x2"]["log_loss"] += log_loss_1x2(prob_1x2, resultado_1x2)
        acumulado["1x2"]["brier"] += brier_score_1x2(prob_1x2, resultado_1x2)

        prob_ou = probabilidad_over_under_2_5(matriz)
        es_over = (partido.goles_local + partido.goles_visitante) > 2.5
        acumulado["over_under_2_5"]["log_loss"] += log_loss_binario(prob_ou["over"], es_over)
        acumulado["over_under_2_5"]["brier"] += brier_score_binario(prob_ou["over"], es_over)

        prob_btts = probabilidad_btts(matriz)
        ambos_marcan = partido.goles_local > 0 and partido.goles_visitante > 0
        acumulado["btts"]["log_loss"] += log_loss_binario(prob_btts["si"], ambos_marcan)
        acumulado["btts"]["brier"] += brier_score_binario(prob_btts["si"], ambos_marcan)

    n = len(jugados)
    return {
        mercado: {clave: valor / n for clave, valor in metricas.items()}
        for mercado, metricas in acumulado.items()
    }
