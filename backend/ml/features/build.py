"""Feature set cerrado de XGBoost (ml-design.md §4, cierre de T012c).

`construir_feature_set` arma una fila por partido con las 5 features de la tabla del
diseño, desdobladas en `_local`/`_visitante` (salvo `h2h_forma`, un único valor desde
la perspectiva del equipo local). Cada feature usa solo partidos estrictamente
anteriores al kickoff del partido en cuestión — nunca información no disponible al
momento real de la predicción.

`fuerza_relativa_ataque`/`fuerza_relativa_defensa` vienen de un Dixon-Coles ya
entrenado, recibido por parámetro (`fuerza_dixon_coles`): este módulo no entrena ni
importa `ml.models.dixon_coles` — cada modelo de `ml/models/*/` es independiente
(Artículo I).

`tiene_historial_suficiente`/`head_to_head_disponible` alimentan el aviso de baja
confiabilidad de RF-010 (`data-model.md`: "Lo calcula quien carga el histórico,
T012b/T012c").

Ver `test_build.py` para el contrato completo.
"""

from __future__ import annotations

import statistics
from typing import TYPE_CHECKING
from uuid import UUID

import pandas as pd

from app.models.partido import EstadoPartido

if TYPE_CHECKING:
    from datetime import datetime

    from app.models.partido import Partido

VENTANA_FORMA = 5
VENTANA_H2H = 5
UMBRAL_HISTORIAL_SUFICIENTE = VENTANA_FORMA

COLUMNAS_FEATURE_SET = [
    "forma_local",
    "forma_visitante",
    "goles_favor_reciente_local",
    "goles_contra_reciente_local",
    "goles_favor_reciente_visitante",
    "goles_contra_reciente_visitante",
    "descanso_dias_local",
    "descanso_dias_visitante",
    "h2h_forma",
    "fuerza_relativa_ataque_local",
    "fuerza_relativa_defensa_local",
    "fuerza_relativa_ataque_visitante",
    "fuerza_relativa_defensa_visitante",
]


def _jugados_antes(partidos: list[Partido], equipo_id: UUID, antes_de: datetime) -> list[Partido]:
    """Partidos jugados de `equipo_id` (local o visitante) anteriores a `antes_de`, del
    más al menos reciente."""
    return sorted(
        (
            p
            for p in partidos
            if p.estado == EstadoPartido.JUGADO
            and p.fecha_kickoff < antes_de
            and equipo_id in (p.equipo_local_id, p.equipo_visitante_id)
        ),
        key=lambda p: p.fecha_kickoff,
        reverse=True,
    )


def _puntos(partido: Partido, equipo_id: UUID) -> int:
    es_local = partido.equipo_local_id == equipo_id
    goles_favor = partido.goles_local if es_local else partido.goles_visitante
    goles_contra = partido.goles_visitante if es_local else partido.goles_local
    if goles_favor > goles_contra:
        return 3
    if goles_favor == goles_contra:
        return 1
    return 0


def _forma(historial: list[Partido], equipo_id: UUID) -> float | None:
    recientes = historial[:VENTANA_FORMA]
    if not recientes:
        return None
    return statistics.mean(_puntos(p, equipo_id) for p in recientes) / 3


def _goles_recientes(
    historial: list[Partido], equipo_id: UUID
) -> tuple[float | None, float | None]:
    recientes = historial[:VENTANA_FORMA]
    if not recientes:
        return None, None
    favor: list[int] = []
    contra: list[int] = []
    for p in recientes:
        es_local = p.equipo_local_id == equipo_id
        favor.append(p.goles_local if es_local else p.goles_visitante)
        contra.append(p.goles_visitante if es_local else p.goles_local)
    return statistics.mean(favor), statistics.mean(contra)


def _descanso_dias(historial: list[Partido], kickoff: datetime) -> float | None:
    if not historial:
        return None
    return (kickoff - historial[0].fecha_kickoff).total_seconds() / 86400


def _historial_h2h(
    partidos: list[Partido], equipo_local_id: UUID, equipo_visitante_id: UUID, antes_de: datetime
) -> list[Partido]:
    rivales = {equipo_local_id, equipo_visitante_id}
    return sorted(
        (
            p
            for p in partidos
            if p.estado == EstadoPartido.JUGADO
            and p.fecha_kickoff < antes_de
            and {p.equipo_local_id, p.equipo_visitante_id} == rivales
        ),
        key=lambda p: p.fecha_kickoff,
        reverse=True,
    )[:VENTANA_H2H]


def _h2h_forma(historial_h2h: list[Partido], equipo_local_id: UUID) -> float | None:
    if not historial_h2h:
        return None
    return statistics.mean(_puntos(p, equipo_local_id) for p in historial_h2h) / 3


def construir_feature_set(
    partidos: list[Partido],
    fuerza_dixon_coles: dict[UUID, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Arma el feature set cerrado de XGBoost — una fila por partido de `partidos`."""
    fuerza_dixon_coles = fuerza_dixon_coles or {}
    filas = []

    for partido in partidos:
        hist_local = _jugados_antes(partidos, partido.equipo_local_id, partido.fecha_kickoff)
        hist_visitante = _jugados_antes(
            partidos, partido.equipo_visitante_id, partido.fecha_kickoff
        )
        historial_h2h = _historial_h2h(
            partidos, partido.equipo_local_id, partido.equipo_visitante_id, partido.fecha_kickoff
        )

        goles_favor_local, goles_contra_local = _goles_recientes(
            hist_local, partido.equipo_local_id
        )
        goles_favor_visitante, goles_contra_visitante = _goles_recientes(
            hist_visitante, partido.equipo_visitante_id
        )

        alpha_local, beta_local = fuerza_dixon_coles.get(partido.equipo_local_id, (None, None))
        alpha_visitante, beta_visitante = fuerza_dixon_coles.get(
            partido.equipo_visitante_id, (None, None)
        )

        filas.append(
            {
                "forma_local": _forma(hist_local, partido.equipo_local_id),
                "forma_visitante": _forma(hist_visitante, partido.equipo_visitante_id),
                "goles_favor_reciente_local": goles_favor_local,
                "goles_contra_reciente_local": goles_contra_local,
                "goles_favor_reciente_visitante": goles_favor_visitante,
                "goles_contra_reciente_visitante": goles_contra_visitante,
                "descanso_dias_local": _descanso_dias(hist_local, partido.fecha_kickoff),
                "descanso_dias_visitante": _descanso_dias(hist_visitante, partido.fecha_kickoff),
                "h2h_forma": _h2h_forma(historial_h2h, partido.equipo_local_id),
                "fuerza_relativa_ataque_local": alpha_local,
                "fuerza_relativa_defensa_local": beta_local,
                "fuerza_relativa_ataque_visitante": alpha_visitante,
                "fuerza_relativa_defensa_visitante": beta_visitante,
            }
        )

    return pd.DataFrame(filas, columns=COLUMNAS_FEATURE_SET)


def tiene_historial_suficiente(historial_equipo: list[Partido]) -> bool:
    """RF-010: un equipo tiene historial suficiente con al menos `UMBRAL_HISTORIAL_SUFICIENTE`
    partidos jugados — el mismo tamaño de ventana que usan `forma`/`goles_recientes`; por
    debajo de eso esas features ya se calculan sobre una muestra incompleta."""
    return len(historial_equipo) >= UMBRAL_HISTORIAL_SUFICIENTE


def head_to_head_disponible(historial_h2h: list[Partido]) -> bool:
    """RF-010: hay head-to-head disponible si existe al menos un enfrentamiento directo previo."""
    return len(historial_h2h) > 0
