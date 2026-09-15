"""Contrato de `ml.evaluation.metrics` — Brier score y log-loss por partido.

Fórmulas fijadas en `ml-design.md` §7 ("Fórmulas de log-loss y Brier score").
Reutilizado tal cual por `003-track-record-publico` (T009 de su `tasks.md`) —
Artículo VIII: una sola implementación, no dos.

Fase Red (Artículo III): `ml.evaluation.metrics` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# --- Mercados binarios (Over/Under 2.5, BTTS) -------------------------------


def test_brier_score_binario_prediccion_perfecta_es_cero() -> None:
    from ml.evaluation.metrics import brier_score_binario

    assert brier_score_binario(prob_predicha=1.0, resultado_real=True) == 0.0


def test_brier_score_binario_prediccion_totalmente_equivocada() -> None:
    from ml.evaluation.metrics import brier_score_binario

    assert brier_score_binario(prob_predicha=0.8, resultado_real=False) == pytest.approx(0.64)


def test_brier_score_binario_probabilidad_intermedia() -> None:
    from ml.evaluation.metrics import brier_score_binario

    assert brier_score_binario(prob_predicha=0.8, resultado_real=True) == pytest.approx(0.04)


def test_log_loss_binario_resultado_positivo() -> None:
    from ml.evaluation.metrics import log_loss_binario

    assert log_loss_binario(prob_predicha=0.8, resultado_real=True) == pytest.approx(
        0.2231435513, abs=1e-9
    )


def test_log_loss_binario_resultado_negativo() -> None:
    from ml.evaluation.metrics import log_loss_binario

    assert log_loss_binario(prob_predicha=0.8, resultado_real=False) == pytest.approx(
        1.6094379124, abs=1e-9
    )


# --- 1X2 (3 clases) ----------------------------------------------------------


def test_brier_score_1x2_prediccion_perfecta_es_cero() -> None:
    from ml.evaluation.metrics import brier_score_1x2

    prob = {"local": 1.0, "empate": 0.0, "visitante": 0.0}
    assert brier_score_1x2(prob_predicha=prob, resultado_real="local") == pytest.approx(0.0)


def test_brier_score_1x2_prediccion_totalmente_equivocada_da_2() -> None:
    """Rango [0, 2] de la definición multi-categoría clásica (Brier, 1950) —
    distinto del rango [0, 1] de los mercados binarios."""
    from ml.evaluation.metrics import brier_score_1x2

    prob = {"local": 0.0, "empate": 0.0, "visitante": 1.0}
    assert brier_score_1x2(prob_predicha=prob, resultado_real="local") == pytest.approx(2.0)


def test_brier_score_1x2_caso_intermedio() -> None:
    from ml.evaluation.metrics import brier_score_1x2

    prob = {"local": 0.5, "empate": 0.3, "visitante": 0.2}
    # (0.5-1)² + (0.3-0)² + (0.2-0)² = 0.25 + 0.09 + 0.04
    assert brier_score_1x2(prob_predicha=prob, resultado_real="local") == pytest.approx(0.38)


def test_log_loss_1x2_toma_la_probabilidad_del_resultado_real() -> None:
    from ml.evaluation.metrics import log_loss_1x2

    prob = {"local": 0.5, "empate": 0.3, "visitante": 0.2}

    assert log_loss_1x2(prob_predicha=prob, resultado_real="local") == pytest.approx(
        0.6931471806, abs=1e-9
    )
    assert log_loss_1x2(prob_predicha=prob, resultado_real="empate") == pytest.approx(
        1.2039728043, abs=1e-9
    )
