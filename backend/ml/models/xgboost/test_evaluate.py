"""Contrato de `ml.models.xgboost.evaluate` (T012e).

Mismo patrón que `ml.models.dixon_coles.evaluate`: delega en
`ml.evaluation.metrics` para log-loss/Brier de los tres mercados, nunca
reimplementa la fórmula (Artículo VIII).

Fase Red (Artículo III): `ml.models.xgboost.evaluate` todavía no existe.
"""

from __future__ import annotations

import pandas as pd
import pytest

pytestmark = pytest.mark.unit

_GRILLA_MINIMA = {"max_depth": [2], "n_estimators": [10], "learning_rate": [0.3]}


def _parametros():
    from ml.models.xgboost.train import entrenar_xgboost

    x = pd.DataFrame({"forma_local": [0.9, 0.9, 0.5, 0.5, 0.1, 0.1] * 3})
    y_1x2 = ["local", "local", "empate", "empate", "visitante", "visitante"] * 3
    y_over = [True, True, True, True, False, False] * 3
    y_btts = [True, True, False, False, False, False] * 3

    return entrenar_xgboost(
        x, y_1x2, y_over, y_btts, x, y_1x2, y_over, y_btts, grilla=_GRILLA_MINIMA
    )


def test_no_hay_filas_de_validacion_falla_explicito() -> None:
    from ml.models.xgboost.evaluate import evaluar_xgboost

    with pytest.raises(ValueError, match="No hay filas"):
        evaluar_xgboost(
            _parametros(),
            pd.DataFrame({"forma_local": []}),
            resultado_1x2=[],
            over_2_5=[],
            btts=[],
        )


def test_devuelve_log_loss_y_brier_para_los_tres_mercados() -> None:
    from ml.models.xgboost.evaluate import evaluar_xgboost

    metricas = evaluar_xgboost(
        _parametros(),
        pd.DataFrame({"forma_local": [0.9, 0.1]}),
        resultado_1x2=["local", "visitante"],
        over_2_5=[True, False],
        btts=[True, False],
    )

    assert set(metricas) == {"1x2", "over_under_2_5", "btts"}
    for mercado in metricas.values():
        assert set(mercado) == {"log_loss", "brier"}
        assert mercado["log_loss"] >= 0.0
        assert 0.0 <= mercado["brier"] <= 2.0


def test_el_brier_de_1x2_coincide_con_ml_evaluation_metrics() -> None:
    from ml.evaluation.metrics import brier_score_1x2
    from ml.models.xgboost.evaluate import evaluar_xgboost
    from ml.models.xgboost.predict import predecir_1x2

    parametros = _parametros()
    features_validacion = pd.DataFrame({"forma_local": [0.9]})

    metricas = evaluar_xgboost(
        parametros, features_validacion, resultado_1x2=["local"], over_2_5=[True], btts=[True]
    )

    prob = predecir_1x2(parametros.modelo_1x2, parametros.clases_1x2, features_validacion)
    esperado = brier_score_1x2(prob, "local")

    assert metricas["1x2"]["brier"] == pytest.approx(esperado)
