"""Capa de combinación de Dixon-Coles y XGBoost (ml-design.md §5).

`p_final = w·p_xgb + (1-w)·p_dc`, un único `w` por reentrenamiento (no por
partido), elegido por grid search sobre el log-loss agregado de los tres
mercados en el set de validación cronológica. `w ≤ W_MAXIMO` (0.85):
Dixon-Coles conserva al menos 15% de peso siempre (`docs/project_spec.md`
§6.4, "ancla interpretable").

`xg_local`/`xg_visitante` de `Predicción` no se ensamblan — vienen directo
de Dixon-Coles (§3), XGBoost no produce una tasa de gol comparable.

`ensemble/` es hermana de `ml/models/`, expone solo este archivo (`plan.md`
§10) — el grid search de `w` vive acá mismo, no en un `train.py` aparte
(Artículo VII).

Ver `backend/tests/unit/test_ensemble.py` para el contrato completo.
"""

from __future__ import annotations

from ml.evaluation.metrics import log_loss_1x2, log_loss_binario

# ml-design.md §5: grilla {0.0, 0.05, ..., 0.85} — el 1.0 del enunciado
# original queda fuera porque violaría el piso mínimo de Dixon-Coles.
W_MAXIMO = 0.85
GRILLA_W_DEFAULT = [round(i * 0.05, 2) for i in range(18)]

MERCADOS = ("1x2", "over_under_2_5", "btts")


def combinar_probabilidades(
    prob_dc: dict[str, float], prob_xgb: dict[str, float], w: float
) -> dict[str, float]:
    """Promedio ponderado clave a clave — sirve para cualquiera de los tres
    mercados, todos son `{clave: probabilidad}`."""
    return {clave: w * prob_xgb[clave] + (1 - w) * prob_dc[clave] for clave in prob_dc}


def _combinar_mercados(
    prob_dc: dict[str, dict[str, float]], prob_xgb: dict[str, dict[str, float]], w: float
) -> dict[str, dict[str, float]]:
    return {
        mercado: combinar_probabilidades(prob_dc[mercado], prob_xgb[mercado], w)
        for mercado in MERCADOS
    }


def predecir_ensamble(
    prob_dc: dict[str, dict[str, float]],
    prob_xgb: dict[str, dict[str, float]],
    xg_local: float,
    xg_visitante: float,
    w: float,
) -> dict[str, dict[str, float] | float]:
    """Combina los tres mercados de `prob_dc`/`prob_xgb` con `w`, y adjunta
    `xg_local`/`xg_visitante` sin tocarlos (vienen directo de Dixon-Coles)."""
    if not 0.0 <= w <= W_MAXIMO:
        raise ValueError(f"w={w} fuera de rango: debe estar en [0.0, {W_MAXIMO}].")

    resultado: dict[str, dict[str, float] | float] = _combinar_mercados(prob_dc, prob_xgb, w)
    resultado["xg_local"] = xg_local
    resultado["xg_visitante"] = xg_visitante
    return resultado


def _log_loss_agregado(
    predicciones_dc: list[dict[str, dict[str, float]]],
    predicciones_xgb: list[dict[str, dict[str, float]]],
    resultado_1x2: list[str],
    over_2_5: list[bool],
    btts: list[bool],
    w: float,
) -> float:
    total = 0.0
    for prob_dc, prob_xgb, r1x2, es_over, ambos_marcan in zip(
        predicciones_dc, predicciones_xgb, resultado_1x2, over_2_5, btts, strict=True
    ):
        combinado = _combinar_mercados(prob_dc, prob_xgb, w)
        total += log_loss_1x2(combinado["1x2"], r1x2)
        total += log_loss_binario(combinado["over_under_2_5"]["over"], es_over)
        total += log_loss_binario(combinado["btts"]["si"], ambos_marcan)
    return total


def elegir_peso_ensamble(
    predicciones_dc: list[dict[str, dict[str, float]]],
    predicciones_xgb: list[dict[str, dict[str, float]]],
    resultado_1x2: list[str],
    over_2_5: list[bool],
    btts: list[bool],
    grilla_w: list[float] | None = None,
) -> float:
    """`w` que minimiza el log-loss agregado de los tres mercados sobre el
    set de validación cronológica — el mismo `w` para todas las
    predicciones de una `version_modelo`, no se recalcula por partido."""
    grilla_w = grilla_w if grilla_w is not None else GRILLA_W_DEFAULT
    if any(w > W_MAXIMO for w in grilla_w):
        raise ValueError(
            f"La grilla no puede superar w={W_MAXIMO} — ml-design.md §5 garantiza "
            "ese piso de peso a Dixon-Coles."
        )

    mejor_w = grilla_w[0]
    mejor_log_loss = float("inf")
    for w in grilla_w:
        perdida = _log_loss_agregado(
            predicciones_dc, predicciones_xgb, resultado_1x2, over_2_5, btts, w
        )
        if perdida < mejor_log_loss:
            mejor_log_loss = perdida
            mejor_w = w
    return mejor_w
