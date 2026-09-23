"""Contrato de `ml.evaluation.baseline_demo` — formateo de la tabla comparativa
para la evidencia de línea base de la defensa EC1.

La orquestación completa (entrenar Dixon-Coles/XGBoost reales, ensamblarlos y
registrar en MLflow) es un script de integración pensado para correrse a mano
contra datos reales (ver `docs/scrum/Auditorias/guia-defensa-ec1.md` bloque 6)
— no se testea aquí, igual que `ml.data.eda._imprimir_reporte`. Lo único puro
y testeable es el formateo de la tabla final.

Fase Red (Artículo III): `ml.evaluation.baseline_demo` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def _metricas(dc_ll: float, xgb_ll: float, ens_ll: float) -> MetricasMercado:  # noqa: F821
    from ml.evaluation.mlflow_tracking import MetricasMercado

    return MetricasMercado(
        log_loss_dixon_coles=dc_ll,
        brier_dixon_coles=dc_ll / 2,
        log_loss_xgboost=xgb_ll,
        brier_xgboost=xgb_ll / 2,
        log_loss_ensamble=ens_ll,
        brier_ensamble=ens_ll / 2,
    )


def test_formatear_tabla_incluye_los_tres_mercados() -> None:
    from ml.evaluation.baseline_demo import formatear_tabla_comparativa

    metricas = {
        "1x2": _metricas(1.05, 1.10, 0.98),
        "over_under_2_5": _metricas(0.68, 0.70, 0.65),
        "btts": _metricas(0.69, 0.66, 0.64),
    }

    tabla = formatear_tabla_comparativa(metricas)

    assert "1x2" in tabla
    assert "over_under_2_5" in tabla
    assert "btts" in tabla


def test_formatear_tabla_muestra_las_tres_columnas_por_mercado() -> None:
    from ml.evaluation.baseline_demo import formatear_tabla_comparativa

    metricas = {"1x2": _metricas(1.05, 1.10, 0.98)}

    tabla = formatear_tabla_comparativa(metricas)

    assert "1.05" in tabla  # Dixon-Coles solo
    assert "1.10" in tabla  # XGBoost solo
    assert "0.98" in tabla  # Ensamble


def test_formatear_tabla_marca_cuando_el_ensamble_no_mejora() -> None:
    """Regla de 'hipótesis fallidas' de la rúbrica: si el ensamble no gana,
    la tabla lo señala en vez de ocultarlo."""
    from ml.evaluation.baseline_demo import formatear_tabla_comparativa

    metricas = {"1x2": _metricas(dc_ll=0.90, xgb_ll=1.20, ens_ll=1.05)}  # ensamble peor que DC solo

    tabla = formatear_tabla_comparativa(metricas)

    assert "no mejora" in tabla.lower() or "peor" in tabla.lower()
