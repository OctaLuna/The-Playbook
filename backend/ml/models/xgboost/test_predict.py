"""Contrato de `ml.models.xgboost.predict` (T012e).

`predecir_1x2` recibe el orden de clases explícito (`clases_1x2`) con el que
`train.py` codificó las etiquetas a enteros — esta versión de `xgboost`
siempre expone `modelo.classes_` como `arange(n_clases)`, nunca las
etiquetas originales, así que el módulo no puede inferir el mapeo solo.

Los mercados binarios entrenan sobre `bool`: `numpy` ordena `[False, True]`
de forma determinística, así que la columna 1 de `predict_proba` es siempre
la probabilidad de la etiqueta positiva — no hace falta guardar el orden.

Fase Red (Artículo III): `ml.models.xgboost.predict` todavía no existe.
"""

from __future__ import annotations

import pandas as pd
import pytest
from xgboost import XGBClassifier

pytestmark = pytest.mark.unit

# Mismo orden que produciría train.py: sorted({"empate", "local", "visitante"}).
_CLASES_1X2 = ("empate", "local", "visitante")


def _modelo_1x2() -> XGBClassifier:
    x = pd.DataFrame({"forma_local": [0.9, 0.9, 0.5, 0.5, 0.1, 0.1] * 3})
    # Codificado en el mismo orden que _CLASES_1X2: empate=0, local=1, visitante=2.
    y = [1, 1, 0, 0, 2, 2] * 3
    modelo = XGBClassifier(max_depth=2, n_estimators=10)
    modelo.fit(x, y)
    return modelo


def _modelo_binario() -> XGBClassifier:
    x = pd.DataFrame({"forma_local": [0.9, 0.9, 0.9, 0.1, 0.1, 0.1] * 3})
    y = [True] * 9 + [False] * 9
    modelo = XGBClassifier(max_depth=2, n_estimators=10)
    modelo.fit(x, y)
    return modelo


def test_predecir_1x2_devuelve_las_tres_claves_sumando_1() -> None:
    from ml.models.xgboost.predict import predecir_1x2

    modelo = _modelo_1x2()
    prob = predecir_1x2(modelo, _CLASES_1X2, pd.DataFrame({"forma_local": [0.9]}))

    assert set(prob) == {"local", "empate", "visitante"}
    assert sum(prob.values()) == pytest.approx(1.0, abs=1e-6)


def test_predecir_1x2_favorece_la_clase_que_el_feature_senala() -> None:
    from ml.models.xgboost.predict import predecir_1x2

    modelo = _modelo_1x2()
    prob_local = predecir_1x2(modelo, _CLASES_1X2, pd.DataFrame({"forma_local": [0.9]}))
    prob_visitante = predecir_1x2(modelo, _CLASES_1X2, pd.DataFrame({"forma_local": [0.1]}))

    assert prob_local["local"] > prob_local["visitante"]
    assert prob_visitante["visitante"] > prob_visitante["local"]


def test_predecir_over_under_devuelve_over_y_under_sumando_1() -> None:
    from ml.models.xgboost.predict import predecir_over_under_2_5

    modelo = _modelo_binario()
    prob = predecir_over_under_2_5(modelo, pd.DataFrame({"forma_local": [0.9]}))

    assert set(prob) == {"over", "under"}
    assert prob["over"] + prob["under"] == pytest.approx(1.0, abs=1e-6)
    assert prob["over"] > prob["under"]


def test_predecir_btts_devuelve_si_y_no_sumando_1() -> None:
    from ml.models.xgboost.predict import predecir_btts

    modelo = _modelo_binario()
    prob = predecir_btts(modelo, pd.DataFrame({"forma_local": [0.1]}))

    assert set(prob) == {"si", "no"}
    assert prob["si"] + prob["no"] == pytest.approx(1.0, abs=1e-6)
    assert prob["no"] > prob["si"]
