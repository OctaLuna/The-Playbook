"""Evaluación de XGBoost vía log-loss/Brier (ml-design.md §7).

Mismo patrón que `ml.models.dixon_coles.evaluate`: reutiliza
`ml.evaluation.metrics` tal cual para los tres mercados (Artículo VIII, una
sola implementación).

Ver `test_evaluate.py` para el contrato completo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ml.evaluation.metrics import (
    brier_score_1x2,
    brier_score_binario,
    log_loss_1x2,
    log_loss_binario,
)
from ml.models.xgboost.predict import predecir_1x2, predecir_btts, predecir_over_under_2_5

if TYPE_CHECKING:
    import pandas as pd

    from ml.models.xgboost.train import ParametrosXGBoost

MERCADOS = ("1x2", "over_under_2_5", "btts")


def evaluar_xgboost(
    parametros: ParametrosXGBoost,
    features_validacion: pd.DataFrame,
    *,
    resultado_1x2: list[str],
    over_2_5: list[bool],
    btts: list[bool],
) -> dict[str, dict[str, float]]:
    """Log-loss y Brier score promedio de `parametros` sobre
    `features_validacion`, uno por mercado (1X2, Over/Under 2.5, BTTS)."""
    n = len(features_validacion)
    if n == 0:
        raise ValueError("No hay filas de validación para evaluar XGBoost.")

    acumulado = {mercado: {"log_loss": 0.0, "brier": 0.0} for mercado in MERCADOS}

    for i in range(n):
        fila = features_validacion.iloc[[i]]

        prob_1x2 = predecir_1x2(parametros.modelo_1x2, parametros.clases_1x2, fila)
        acumulado["1x2"]["log_loss"] += log_loss_1x2(prob_1x2, resultado_1x2[i])
        acumulado["1x2"]["brier"] += brier_score_1x2(prob_1x2, resultado_1x2[i])

        prob_ou = predecir_over_under_2_5(parametros.modelo_over_under_2_5, fila)
        acumulado["over_under_2_5"]["log_loss"] += log_loss_binario(prob_ou["over"], over_2_5[i])
        acumulado["over_under_2_5"]["brier"] += brier_score_binario(prob_ou["over"], over_2_5[i])

        prob_btts = predecir_btts(parametros.modelo_btts, fila)
        acumulado["btts"]["log_loss"] += log_loss_binario(prob_btts["si"], btts[i])
        acumulado["btts"]["brier"] += brier_score_binario(prob_btts["si"], btts[i])

    return {
        mercado: {clave: valor / n for clave, valor in metricas.items()}
        for mercado, metricas in acumulado.items()
    }
