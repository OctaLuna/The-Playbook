"""Ajuste de XGBoost sobre el feature set cerrado de T012c (ml-design.md §4).

Tres modelos independientes, uno por mercado: 1X2 (3 clases), Over/Under 2.5
y BTTS (binarios). `ml-design.md` §4 fija los objetivos, no los
hiperparámetros — se eligen acá por búsqueda en grilla sobre el log-loss del
set de validación cronológica.

Recibe el feature set ya construido (`ml.features.build`, T012c) y las
etiquetas ya derivadas, entrenamiento y validación por separado: el split
cronológico es responsabilidad de `ml.evaluation.split` (Artículo VIII, no
reimplementado acá) — este módulo se mantiene independiente de `ml.features`,
igual que `ml.models.dixon_coles` (ml-design.md §2: cada etapa del pipeline
lee la salida de la anterior, no la reconstruye).

Esta versión de `xgboost` exige que `y` ya venga codificado a enteros
`0..n-1` — `XGBClassifier.classes_` siempre devuelve esos índices, nunca las
etiquetas originales (a diferencia de versiones previas de `scikit-learn`,
que codificaban por dentro). Las 3 clases de 1X2 (`"local"`/`"empate"`/
`"visitante"`) se codifican acá y el orden se devuelve en `ParametrosXGBoost.
clases_1x2` para que `predict.py` lo use al decodificar. Los mercados
binarios entrenan directo sobre `bool`: `False`/`True` ya son `0`/`1`.

Ver `test_train.py` para el contrato completo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sklearn.metrics import log_loss
from sklearn.model_selection import ParameterGrid
from xgboost import XGBClassifier

if TYPE_CHECKING:
    import pandas as pd

# ml-design.md §4: no fija valores, solo pide grid search sobre el log-loss
# de validación cronológica dentro de este módulo.
GRILLA_HIPERPARAMETROS_DEFAULT = {
    "max_depth": [2, 3, 4],
    "n_estimators": [50, 100],
    "learning_rate": [0.05, 0.1],
}


@dataclass(frozen=True)
class ParametrosXGBoost:
    modelo_1x2: XGBClassifier
    clases_1x2: tuple[str, ...]
    modelo_over_under_2_5: XGBClassifier
    modelo_btts: XGBClassifier
    hiperparametros_1x2: dict
    hiperparametros_over_under: dict
    hiperparametros_btts: dict


def _mejor_modelo(
    x_entrenamiento: pd.DataFrame,
    y_entrenamiento_codificado: list[int],
    x_validacion: pd.DataFrame,
    y_validacion_codificado: list[int],
    n_clases: int,
    grilla: dict[str, list],
) -> tuple[XGBClassifier, dict]:
    """Ajusta un `XGBClassifier` por cada combinación de `grilla` sobre
    etiquetas ya codificadas `0..n_clases-1`, y se queda con la de menor
    log-loss sobre `x_validacion`/`y_validacion_codificado`."""
    todas_las_clases = list(range(n_clases))
    mejor_log_loss = float("inf")
    mejor_modelo: XGBClassifier | None = None
    mejor_params: dict | None = None

    for params in ParameterGrid(grilla):
        modelo = XGBClassifier(**params)
        modelo.fit(x_entrenamiento, y_entrenamiento_codificado)
        probabilidades = modelo.predict_proba(x_validacion)
        perdida = log_loss(y_validacion_codificado, probabilidades, labels=todas_las_clases)
        if perdida < mejor_log_loss:
            mejor_log_loss = perdida
            mejor_modelo = modelo
            mejor_params = params

    if mejor_modelo is None or mejor_params is None:
        raise ValueError("La grilla de hiperparámetros no tiene ninguna combinación.")
    return mejor_modelo, mejor_params


def entrenar_xgboost(
    features_entrenamiento: pd.DataFrame,
    resultado_1x2_entrenamiento: list[str],
    over_2_5_entrenamiento: list[bool],
    btts_entrenamiento: list[bool],
    features_validacion: pd.DataFrame,
    resultado_1x2_validacion: list[str],
    over_2_5_validacion: list[bool],
    btts_validacion: list[bool],
    grilla: dict[str, list] | None = None,
) -> ParametrosXGBoost:
    """Entrena los tres modelos de mercado, cada uno con la mejor
    combinación de `grilla` (default `GRILLA_HIPERPARAMETROS_DEFAULT`) según
    el log-loss de validación cronológica."""
    grilla = grilla or GRILLA_HIPERPARAMETROS_DEFAULT

    clases_1x2 = tuple(sorted(set(resultado_1x2_entrenamiento) | set(resultado_1x2_validacion)))
    indice_1x2 = {clase: i for i, clase in enumerate(clases_1x2)}
    y_1x2_entrenamiento = [indice_1x2[v] for v in resultado_1x2_entrenamiento]
    y_1x2_validacion = [indice_1x2[v] for v in resultado_1x2_validacion]

    modelo_1x2, hiperparametros_1x2 = _mejor_modelo(
        features_entrenamiento,
        y_1x2_entrenamiento,
        features_validacion,
        y_1x2_validacion,
        len(clases_1x2),
        grilla,
    )
    modelo_over_under, hiperparametros_over_under = _mejor_modelo(
        features_entrenamiento,
        [int(v) for v in over_2_5_entrenamiento],
        features_validacion,
        [int(v) for v in over_2_5_validacion],
        2,
        grilla,
    )
    modelo_btts, hiperparametros_btts = _mejor_modelo(
        features_entrenamiento,
        [int(v) for v in btts_entrenamiento],
        features_validacion,
        [int(v) for v in btts_validacion],
        2,
        grilla,
    )

    return ParametrosXGBoost(
        modelo_1x2=modelo_1x2,
        clases_1x2=clases_1x2,
        modelo_over_under_2_5=modelo_over_under,
        modelo_btts=modelo_btts,
        hiperparametros_1x2=hiperparametros_1x2,
        hiperparametros_over_under=hiperparametros_over_under,
        hiperparametros_btts=hiperparametros_btts,
    )
