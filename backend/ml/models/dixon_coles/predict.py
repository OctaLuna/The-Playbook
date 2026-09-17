"""Predicción de mercados a partir de un Dixon-Coles ya entrenado (ml-design.md §3).

`tasas_esperadas` devuelve `λ`/`μ` — también son `xg_local`/`xg_visitante` de
`Predicción`, no un xG a nivel de tiro. `matriz_probabilidad_marcador` arma la
Poisson bivariada con la corrección `τ` del paper original. 1X2, Over/Under
2.5 y BTTS no tienen fórmula cerrada propia: los tres se obtienen sumando esa
misma matriz sobre los rangos correspondientes.

Ver `test_predict.py` para el contrato completo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import poisson

if TYPE_CHECKING:
    from uuid import UUID

    from ml.models.dixon_coles.train import ParametrosDixonColes

# Cota superior de la matriz de marcador exacto. `poisson.pmf` es
# numéricamente despreciable más allá de esto para los `λ`/`μ` de fútbol
# (rara vez > 4), así que la matriz sigue sumando ~1 sin necesitar más filas.
MAX_GOLES = 10


def tau_dixon_coles(
    goles_local: int, goles_visitante: int, lam: float, mu: float, rho: float
) -> float:
    """Corrección de dependencia de Dixon-Coles (ml-design.md §3): solo actúa
    sobre los 4 marcadores bajos que el paper corrige, `1.0` en el resto."""
    if goles_local == 0 and goles_visitante == 0:
        return 1 - lam * mu * rho
    if goles_local == 0 and goles_visitante == 1:
        return 1 + lam * rho
    if goles_local == 1 and goles_visitante == 0:
        return 1 + mu * rho
    if goles_local == 1 and goles_visitante == 1:
        return 1 - rho
    return 1.0


def tasas_esperadas(
    parametros: ParametrosDixonColes, equipo_local_id: UUID, equipo_visitante_id: UUID
) -> tuple[float, float]:
    """`λ` (goles esperados del local) = `exp(alpha_i + beta_j + gamma)`;
    `μ` (visitante) = `exp(alpha_j + beta_i)` (ml-design.md §3)."""
    alpha_local = parametros.alpha[equipo_local_id]
    beta_local = parametros.beta[equipo_local_id]
    alpha_visitante = parametros.alpha[equipo_visitante_id]
    beta_visitante = parametros.beta[equipo_visitante_id]

    lam = np.exp(alpha_local + beta_visitante + parametros.gamma)
    mu = np.exp(alpha_visitante + beta_local)
    return float(lam), float(mu)


def matriz_probabilidad_marcador(
    lam: float, mu: float, rho: float, max_goles: int = MAX_GOLES
) -> np.ndarray:
    """Matriz `[x, y]` de probabilidad del marcador exacto local `x` -
    visitante `y`: Poisson bivariada con la corrección `τ` aplicada solo a
    los 4 marcadores bajos que cubre.

    Renormalizada para sumar exactamente 1: la corrección `τ` no es
    conservativa de probabilidad para todo `λ`/`μ`/rho, y truncar en
    `max_goles` ya le resta una masa (despreciable pero no nula) a la cola.
    Los mercados que se derivan de esta matriz (1X2, O/U 2.5, BTTS) deben
    sumar exactamente 1 para que `sklearn.metrics.log_loss` (ml.evaluation.metrics,
    Artículo VIII) no los rechace por no ser una distribución válida.
    """
    goles = np.arange(max_goles + 1)
    matriz = np.outer(poisson.pmf(goles, lam), poisson.pmf(goles, mu))
    for x in (0, 1):
        for y in (0, 1):
            matriz[x, y] *= tau_dixon_coles(x, y, lam, mu, rho)
    return matriz / matriz.sum()


def probabilidad_1x2(matriz: np.ndarray) -> dict[str, float]:
    """Suma la matriz de marcador sobre local > visitante, empate y
    visitante > local — no hay fórmula cerrada separada (ml-design.md §3)."""
    return {
        "local": float(np.tril(matriz, -1).sum()),
        "empate": float(np.trace(matriz)),
        "visitante": float(np.triu(matriz, 1).sum()),
    }


def probabilidad_over_under_2_5(matriz: np.ndarray) -> dict[str, float]:
    """Suma la matriz sobre los marcadores cuyo total de goles supera 2.5."""
    total_goles = np.add.outer(np.arange(matriz.shape[0]), np.arange(matriz.shape[1]))
    over = float(matriz[total_goles > 2.5].sum())
    return {"over": over, "under": 1.0 - over}


def probabilidad_btts(matriz: np.ndarray) -> dict[str, float]:
    """Suma la matriz sobre los marcadores donde ambos equipos anotan
    (`x ≥ 1` y `y ≥ 1`)."""
    si = float(matriz[1:, 1:].sum())
    return {"si": si, "no": 1.0 - si}
