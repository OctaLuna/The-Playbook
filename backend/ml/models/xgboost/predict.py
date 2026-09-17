"""Predicción de mercados a partir de un XGBoost ya entrenado (ml-design.md §4).

`XGBClassifier.classes_` en esta versión de `xgboost` siempre devuelve
`arange(n_clases)` (índices enteros), nunca las etiquetas originales — el
ajuste exige codificarlas a enteros antes de entrenar (ver `train.py`). Por
eso `predecir_1x2` recibe el orden de clases explícito que `train.py`
guardó, en vez de leerlo del modelo.

Los mercados binarios (Over/Under 2.5, BTTS) se entrenan sobre etiquetas
`bool` — `numpy` ordena `[False, True]` de forma determinística, así que la
columna 1 de `predict_proba` es siempre la probabilidad de la etiqueta
positiva (ver `test_predict.py`), sin necesitar guardar el orden aparte.

Ver `test_predict.py` para el contrato completo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from xgboost import XGBClassifier


def predecir_1x2(
    modelo: XGBClassifier, clases_1x2: tuple[str, ...], features: pd.DataFrame
) -> dict[str, float]:
    """`{"local": ..., "empate": ..., "visitante": ...}` — `clases_1x2` es el
    orden con el que `train.py` codificó las etiquetas, columna a columna."""
    probabilidades = modelo.predict_proba(features)[0]
    return {clase: float(prob) for clase, prob in zip(clases_1x2, probabilidades, strict=True)}


def predecir_over_under_2_5(modelo: XGBClassifier, features: pd.DataFrame) -> dict[str, float]:
    """`{"over": ..., "under": ...}`; el modelo se entrena sobre `es_over: bool`,
    así que la columna 1 (`True`) es siempre `"over"`."""
    prob_over = float(modelo.predict_proba(features)[0][1])
    return {"over": prob_over, "under": 1.0 - prob_over}


def predecir_btts(modelo: XGBClassifier, features: pd.DataFrame) -> dict[str, float]:
    """`{"si": ..., "no": ...}`; el modelo se entrena sobre `ambos_marcan: bool`,
    así que la columna 1 (`True`) es siempre `"si"`."""
    prob_si = float(modelo.predict_proba(features)[0][1])
    return {"si": prob_si, "no": 1.0 - prob_si}
