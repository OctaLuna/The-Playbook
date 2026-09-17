"""Contrato de `ml.ensemble.predict` (T012).

Ver `ml-design.md` §5: combina Dixon-Coles (`p_dc`) y XGBoost (`p_xgb`) para
el mismo mercado por promedio ponderado — `p_final = w·p_xgb + (1-w)·p_dc`.
`w` se elige una sola vez por reentrenamiento (no por partido) por grid
search sobre el log-loss **agregado de los tres mercados** en el set de
validación cronológica, con `w ≤ 0.85` — Dixon-Coles conserva como mínimo
15% de peso siempre (`docs/project_spec.md` §6.4, "ancla interpretable").

`xg_local`/`xg_visitante` de `Predicción` **no** se ensamblan: vienen
directo de Dixon-Coles (§3), así que `predecir_ensamble` los recibe y
devuelve tal cual, sin tocarlos.

`ensemble/` es hermana de `models/`, expone solo `predict.py` (`plan.md`
§10) — el grid search de `w` vive en el mismo archivo, no en un `train.py`
aparte (Artículo VII). Estas pruebas viven en `backend/tests/unit/` por
instrucción explícita del "Orden de creación de archivos" de `plan.md`, a
diferencia de `ml.models.dixon_coles`/`ml.models.xgboost`, cuyos tests están
co-ubicados en `backend/ml/`.

Fase Red (Artículo III): `ml.ensemble.predict` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def _mercados(local: float, empate: float, visitante: float, over: float, si: float) -> dict:
    return {
        "1x2": {"local": local, "empate": empate, "visitante": visitante},
        "over_under_2_5": {"over": over, "under": 1.0 - over},
        "btts": {"si": si, "no": 1.0 - si},
    }


class TestCombinarProbabilidades:
    def test_promedio_ponderado_por_clave(self) -> None:
        from ml.ensemble.predict import combinar_probabilidades

        prob_dc = {"local": 0.5, "empate": 0.3, "visitante": 0.2}
        prob_xgb = {"local": 0.6, "empate": 0.1, "visitante": 0.3}

        combinado = combinar_probabilidades(prob_dc, prob_xgb, w=0.4)

        assert combinado["local"] == pytest.approx(0.4 * 0.6 + 0.6 * 0.5)
        assert combinado["empate"] == pytest.approx(0.4 * 0.1 + 0.6 * 0.3)
        assert combinado["visitante"] == pytest.approx(0.4 * 0.3 + 0.6 * 0.2)

    def test_w_0_devuelve_dixon_coles_puro(self) -> None:
        from ml.ensemble.predict import combinar_probabilidades

        prob_dc = {"over": 0.7, "under": 0.3}
        prob_xgb = {"over": 0.2, "under": 0.8}

        assert combinar_probabilidades(prob_dc, prob_xgb, w=0.0) == pytest.approx(prob_dc)

    def test_w_085_devuelve_mayormente_xgboost(self) -> None:
        from ml.ensemble.predict import W_MAXIMO, combinar_probabilidades

        prob_dc = {"si": 0.5, "no": 0.5}
        prob_xgb = {"si": 1.0, "no": 0.0}

        combinado = combinar_probabilidades(prob_dc, prob_xgb, w=W_MAXIMO)

        assert combinado["si"] == pytest.approx(0.85 * 1.0 + 0.15 * 0.5)


class TestPredecirEnsamble:
    def test_combina_los_tres_mercados_y_no_toca_el_xg(self) -> None:
        from ml.ensemble.predict import predecir_ensamble

        prob_dc = _mercados(0.5, 0.3, 0.2, 0.4, 0.5)
        prob_xgb = _mercados(0.6, 0.1, 0.3, 0.6, 0.7)

        resultado = predecir_ensamble(prob_dc, prob_xgb, xg_local=1.8, xg_visitante=0.9, w=0.5)

        assert resultado["1x2"]["local"] == pytest.approx(0.5 * 0.6 + 0.5 * 0.5)
        assert resultado["over_under_2_5"]["over"] == pytest.approx(0.5 * 0.6 + 0.5 * 0.4)
        assert resultado["btts"]["si"] == pytest.approx(0.5 * 0.7 + 0.5 * 0.5)
        assert resultado["xg_local"] == pytest.approx(1.8)
        assert resultado["xg_visitante"] == pytest.approx(0.9)

    def test_w_fuera_de_rango_falla_explicito(self) -> None:
        from ml.ensemble.predict import predecir_ensamble

        prob_dc = _mercados(0.5, 0.3, 0.2, 0.4, 0.5)
        prob_xgb = _mercados(0.6, 0.1, 0.3, 0.6, 0.7)

        with pytest.raises(ValueError, match="w"):
            predecir_ensamble(prob_dc, prob_xgb, xg_local=1.0, xg_visitante=1.0, w=0.9)


class TestElegirPesoEnsamble:
    def test_favorece_xgboost_cuando_xgboost_predice_mejor(self) -> None:
        """XGBoost acierta con confianza, Dixon-Coles es uniforme (no aporta
        nada): el log-loss agregado baja monótono con `w`, así que la
        búsqueda debe quedarse en el techo permitido, `W_MAXIMO`."""
        from ml.ensemble.predict import W_MAXIMO, elegir_peso_ensamble

        uniforme = _mercados(1 / 3, 1 / 3, 1 / 3, 0.5, 0.5)
        certero_local = _mercados(0.9, 0.05, 0.05, 0.9, 0.9)
        certero_visitante = _mercados(0.05, 0.05, 0.9, 0.1, 0.1)

        predicciones_dc = [uniforme, uniforme]
        predicciones_xgb = [certero_local, certero_visitante]
        resultado_1x2 = ["local", "visitante"]
        over_2_5 = [True, False]
        btts = [True, False]

        w = elegir_peso_ensamble(predicciones_dc, predicciones_xgb, resultado_1x2, over_2_5, btts)

        assert w == pytest.approx(W_MAXIMO)

    def test_favorece_dixon_coles_cuando_dixon_coles_predice_mejor(self) -> None:
        from ml.ensemble.predict import elegir_peso_ensamble

        certero_local = _mercados(0.9, 0.05, 0.05, 0.9, 0.9)
        certero_visitante = _mercados(0.05, 0.05, 0.9, 0.1, 0.1)
        uniforme = _mercados(1 / 3, 1 / 3, 1 / 3, 0.5, 0.5)

        predicciones_dc = [certero_local, certero_visitante]
        predicciones_xgb = [uniforme, uniforme]
        resultado_1x2 = ["local", "visitante"]
        over_2_5 = [True, False]
        btts = [True, False]

        w = elegir_peso_ensamble(predicciones_dc, predicciones_xgb, resultado_1x2, over_2_5, btts)

        assert w == pytest.approx(0.0)

    def test_una_grilla_por_encima_de_w_maximo_falla_explicito(self) -> None:
        from ml.ensemble.predict import elegir_peso_ensamble

        uniforme = _mercados(1 / 3, 1 / 3, 1 / 3, 0.5, 0.5)

        with pytest.raises(ValueError, match="La grilla no puede superar"):
            elegir_peso_ensamble(
                [uniforme], [uniforme], ["local"], [True], [True], grilla_w=[0.0, 0.9]
            )
