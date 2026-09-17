"""Contrato de `ml.models.xgboost.train` (T012e).

Ver `ml-design.md` §4: tres modelos independientes, uno por mercado — 1X2
(`multi:softprob`, 3 clases), Over/Under 2.5 y BTTS (`binary:logistic` cada
uno). Los hiperparámetros no vienen fijados en el diseño: se eligen acá por
búsqueda en grilla sobre el log-loss del set de validación cronológica.

`entrenar_xgboost` recibe el feature set ya construido (`ml.features.build`,
T012c) y las etiquetas ya derivadas, entrenamiento y validación por
separado — el split cronológico es responsabilidad de `ml.evaluation.split`
(Artículo VIII: no reimplementarlo acá), no de este módulo.

Fase Red (Artículo III): `ml.models.xgboost.train` todavía no existe.
"""

from __future__ import annotations

import pandas as pd
import pytest

pytestmark = pytest.mark.unit


def _features(valores: list[float]) -> pd.DataFrame:
    """Un único feature numérico — alcanza para ejercitar el contrato de
    entrenamiento sin depender del feature set real de 13 columnas."""
    return pd.DataFrame({"forma_local": valores})


def _dataset_separable() -> tuple[
    pd.DataFrame, list[str], list[bool], list[bool], pd.DataFrame, list[str], list[bool], list[bool]
]:
    """Un feature que separa perfectamente los 3 resultados de 1X2 y ambos
    mercados binarios, para que cualquier hiperparámetro razonable de la
    grilla lo aprenda y el test no dependa de una elección particular."""
    x_entrenamiento = _features([0.9, 0.85, 0.8, 0.5, 0.45, 0.55, 0.1, 0.15, 0.05] * 3)
    y_1x2_entrenamiento = [
        "local",
        "local",
        "local",
        "empate",
        "empate",
        "empate",
        "visitante",
        "visitante",
        "visitante",
    ] * 3
    y_over_entrenamiento = [True, True, True, True, True, False, False, False, False] * 3
    y_btts_entrenamiento = [True, True, True, False, False, False, False, False, True] * 3

    x_validacion = _features([0.88, 0.52, 0.08])
    y_1x2_validacion = ["local", "empate", "visitante"]
    y_over_validacion = [True, True, False]
    y_btts_validacion = [True, False, False]

    return (
        x_entrenamiento,
        y_1x2_entrenamiento,
        y_over_entrenamiento,
        y_btts_entrenamiento,
        x_validacion,
        y_1x2_validacion,
        y_over_validacion,
        y_btts_validacion,
    )


_GRILLA_MINIMA = {"max_depth": [2], "n_estimators": [10], "learning_rate": [0.3]}


def test_devuelve_un_modelo_ajustado_por_cada_mercado() -> None:
    from xgboost import XGBClassifier

    from ml.models.xgboost.train import entrenar_xgboost

    (x_train, y1x2_train, yover_train, ybtts_train, x_val, y1x2_val, yover_val, ybtts_val) = (
        _dataset_separable()
    )

    parametros = entrenar_xgboost(
        x_train,
        y1x2_train,
        yover_train,
        ybtts_train,
        x_val,
        y1x2_val,
        yover_val,
        ybtts_val,
        grilla=_GRILLA_MINIMA,
    )

    assert isinstance(parametros.modelo_1x2, XGBClassifier)
    assert isinstance(parametros.modelo_over_under_2_5, XGBClassifier)
    assert isinstance(parametros.modelo_btts, XGBClassifier)


def test_el_modelo_1x2_conoce_las_tres_clases() -> None:
    from ml.models.xgboost.train import entrenar_xgboost

    (x_train, y1x2_train, yover_train, ybtts_train, x_val, y1x2_val, yover_val, ybtts_val) = (
        _dataset_separable()
    )

    parametros = entrenar_xgboost(
        x_train,
        y1x2_train,
        yover_train,
        ybtts_train,
        x_val,
        y1x2_val,
        yover_val,
        ybtts_val,
        grilla=_GRILLA_MINIMA,
    )

    assert set(parametros.clases_1x2) == {"local", "empate", "visitante"}


def test_la_busqueda_en_grilla_elige_entre_mas_de_una_combinacion() -> None:
    """No hay un hiperparámetro fijado en `ml-design.md` §4 — la elección
    tiene que salir de comparar log-loss de validación entre combinaciones
    reales de la grilla, no de un único valor hardcodeado."""
    from ml.models.xgboost.train import entrenar_xgboost

    (x_train, y1x2_train, yover_train, ybtts_train, x_val, y1x2_val, yover_val, ybtts_val) = (
        _dataset_separable()
    )
    grilla_amplia = {"max_depth": [2, 4], "n_estimators": [10, 20], "learning_rate": [0.1, 0.3]}

    parametros = entrenar_xgboost(
        x_train,
        y1x2_train,
        yover_train,
        ybtts_train,
        x_val,
        y1x2_val,
        yover_val,
        ybtts_val,
        grilla=grilla_amplia,
    )

    assert parametros.hiperparametros_1x2["max_depth"] in grilla_amplia["max_depth"]
    assert parametros.hiperparametros_1x2["n_estimators"] in grilla_amplia["n_estimators"]
    assert parametros.hiperparametros_1x2["learning_rate"] in grilla_amplia["learning_rate"]


def test_usa_la_grilla_default_cuando_no_se_pasa_una() -> None:
    from ml.models.xgboost.train import GRILLA_HIPERPARAMETROS_DEFAULT, entrenar_xgboost

    (x_train, y1x2_train, yover_train, ybtts_train, x_val, y1x2_val, yover_val, ybtts_val) = (
        _dataset_separable()
    )

    parametros = entrenar_xgboost(
        x_train, y1x2_train, yover_train, ybtts_train, x_val, y1x2_val, yover_val, ybtts_val
    )

    assert (
        parametros.hiperparametros_1x2["max_depth"] in GRILLA_HIPERPARAMETROS_DEFAULT["max_depth"]
    )
