"""Brier score y log-loss por partido, para los tres mercados probabilísticos.

Fórmulas fijadas en `specs/001-prediccion-partido/ml-design.md` §7. Reutilizado
tal cual por `003-track-record-publico` (Artículo VIII: una sola
implementación).
"""

from __future__ import annotations

from sklearn.metrics import log_loss as _sklearn_log_loss

CLAVES_1X2 = ("local", "empate", "visitante")


def brier_score_binario(prob_predicha: float, resultado_real: bool) -> float:
    """`(p - o)²` para un mercado binario (Over/Under 2.5, BTTS)."""
    o = 1.0 if resultado_real else 0.0
    return (prob_predicha - o) ** 2


def log_loss_binario(prob_predicha: float, resultado_real: bool) -> float:
    """Log-loss binario vía `sklearn.metrics.log_loss` (Artículo VIII)."""
    o = 1 if resultado_real else 0
    return float(_sklearn_log_loss([o], [[1 - prob_predicha, prob_predicha]], labels=[0, 1]))


def brier_score_1x2(prob_predicha: dict[str, float], resultado_real: str) -> float:
    """Brier score multi-categoría clásico (Brier, 1950): suma sobre las 3
    clases de `(p_k - o_k)²`, con `o` one-hot. Rango `[0, 2]`."""
    return sum(
        (prob - (1.0 if clave == resultado_real else 0.0)) ** 2
        for clave, prob in prob_predicha.items()
    )


def log_loss_1x2(prob_predicha: dict[str, float], resultado_real: str) -> float:
    """Log-loss de 1X2 vía `sklearn.metrics.log_loss`.

    `sklearn.metrics.log_loss` ignora el orden de `labels` para alinear las
    columnas de `y_pred` y asume orden lexicográfico sin importar qué se le
    pase (comportamiento no documentado en la firma, solo advertido en
    runtime) — por eso acá se ordenan las claves explícitamente en vez de
    usar el orden fijo de `CLAVES_1X2`.
    """
    claves_ordenadas = sorted(CLAVES_1X2)
    fila = [[prob_predicha[clave] for clave in claves_ordenadas]]
    return float(_sklearn_log_loss([resultado_real], fila, labels=claves_ordenadas))
