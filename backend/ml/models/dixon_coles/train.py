"""Ajuste de Dixon-Coles por máxima verosimilitud (ml-design.md §3).

`entrenar_dixon_coles` optimiza el log-likelihood negativo sobre alpha/beta/
gamma/rho con `scipy.optimize.minimize` — `statsmodels` no trae Dixon-Coles
como función lista, así que este es el enfoque estándar de la literatura
(ml-design.md §3). `ξ` (decaimiento temporal) es un hiperparámetro de
configuración, nunca se ajusta por optimización.

La restricción de identificabilidad "suma de alpha = 0" se impone por
reparametrización en vez de con un optimizador restringido: el último equipo
del orden nunca se optimiza directamente, se deriva como menos la suma de
los demás, así que la restricción se cumple exactamente en cualquier punto
de la búsqueda, no solo en el óptimo.

Ver `test_train.py` para el contrato completo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

from app.models.partido import EstadoPartido
from ml.models.dixon_coles.predict import tau_dixon_coles

if TYPE_CHECKING:
    from datetime import datetime

    from app.models.partido import Partido

# ml-design.md §3: valor típico reportado en la literatura de aplicación de
# Dixon-Coles a ligas europeas (≈ media vida de un año).
XI_DEFAULT = 0.0018


@dataclass(frozen=True)
class ParametrosDixonColes:
    """Parámetros ajustados del modelo — uno por equipo para `alpha`/`beta`,
    globales para `gamma`/`rho`/`xi` (ml-design.md §3)."""

    alpha: dict[UUID, float]
    beta: dict[UUID, float]
    gamma: float
    rho: float
    xi: float


def entrenar_dixon_coles(
    partidos: list[Partido],
    *,
    xi: float = XI_DEFAULT,
    fecha_referencia: datetime | None = None,
) -> ParametrosDixonColes:
    """Ajusta alpha/beta/gamma/rho sobre los partidos jugados de `partidos`.

    `fecha_referencia` es el punto desde el que se cuentan los "días desde
    el partido" del decaimiento `peso = exp(-ξ·días_desde_el_partido)`; por
    default es el kickoff más reciente del propio set de entrenamiento.
    """
    jugados = [p for p in partidos if p.estado == EstadoPartido.JUGADO]
    if not jugados:
        raise ValueError("No hay partidos jugados para entrenar Dixon-Coles.")

    equipos = sorted(
        {p.equipo_local_id for p in jugados} | {p.equipo_visitante_id for p in jugados},
        key=str,
    )
    n = len(equipos)
    indice = {equipo_id: i for i, equipo_id in enumerate(equipos)}

    referencia = fecha_referencia or max(p.fecha_kickoff for p in jugados)
    pesos = np.array([np.exp(-xi * (referencia - p.fecha_kickoff).days) for p in jugados])

    def _desempaquetar(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
        alpha = np.append(x[: n - 1], -x[: n - 1].sum())
        beta = x[n - 1 : 2 * n - 1]
        gamma, rho = x[2 * n - 1], x[2 * n]
        return alpha, beta, gamma, rho

    def _neg_log_verosimilitud(x: np.ndarray) -> float:
        alpha, beta, gamma, rho = _desempaquetar(x)
        total = 0.0
        for partido, peso in zip(jugados, pesos, strict=True):
            i, j = indice[partido.equipo_local_id], indice[partido.equipo_visitante_id]
            lam = np.exp(alpha[i] + beta[j] + gamma)
            mu = np.exp(alpha[j] + beta[i])
            tau_val = max(
                tau_dixon_coles(partido.goles_local, partido.goles_visitante, lam, mu, rho),
                1e-10,
            )
            log_p = (
                np.log(tau_val)
                + poisson.logpmf(partido.goles_local, lam)
                + poisson.logpmf(partido.goles_visitante, mu)
            )
            total -= peso * log_p
        return float(total)

    x0 = np.concatenate([np.zeros(n - 1), np.zeros(n), [0.1], [0.0]])
    resultado = minimize(_neg_log_verosimilitud, x0, method="L-BFGS-B")
    alpha, beta, gamma, rho = _desempaquetar(resultado.x)

    return ParametrosDixonColes(
        alpha=dict(zip(equipos, alpha.tolist(), strict=True)),
        beta=dict(zip(equipos, beta.tolist(), strict=True)),
        gamma=float(gamma),
        rho=float(rho),
        xi=xi,
    )
