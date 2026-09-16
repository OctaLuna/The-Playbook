"""Carga de CSV de Football-Data.co.uk (ml-design.md §1).

Parsea el mapeo de columnas fijado en el diseño: `Date`, `HomeTeam`, `AwayTeam`,
`FTHG`, `FTAG`. Nunca lee columnas de cuotas (`B365*` y afines) — el Artículo V
(Independencia del Mercado) se cumple por omisión: este módulo simplemente no las
conoce, no hace falta un filtro explícito para algo que nunca se lee.

Ver `test_loader.py` para el contrato completo.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from app.models.partido import Liga

if TYPE_CHECKING:
    from os import PathLike

# ml-design.md §1: el CSV no trae hora de kickoff — se usa 15:00 hora local de la
# liga como convención hasta tener el dato operativo real.
_HORA_KICKOFF_CONVENCIONAL = (15, 0)

_ZONA_HORARIA_POR_LIGA: dict[Liga, str] = {
    Liga.PREMIER_LEAGUE: "Europe/London",
    Liga.LALIGA: "Europe/Madrid",
    Liga.SERIE_A: "Europe/Rome",
    Liga.BUNDESLIGA: "Europe/Berlin",
    Liga.LIGUE_1: "Europe/Paris",
}

# Football-Data.co.uk usa dd/mm/yyyy en temporadas recientes y dd/mm/yy en las viejas.
_FORMATOS_FECHA = ("%d/%m/%Y", "%d/%m/%y")


class FilaPartidoInvalidaError(ValueError):
    """Una fila del CSV no tiene una fecha reconocible o le falta una columna requerida."""


@dataclass(frozen=True)
class RegistroPartido:
    """Un partido histórico ya parseado, sin ninguna referencia a cuotas."""

    fecha_kickoff: datetime
    equipo_local_raw: str
    equipo_visitante_raw: str
    goles_local: int
    goles_visitante: int


def _parsear_fecha(fecha_cruda: str, liga: Liga) -> datetime:
    for formato in _FORMATOS_FECHA:
        try:
            fecha = datetime.strptime(fecha_cruda, formato)
            break
        except ValueError:
            continue
    else:
        raise FilaPartidoInvalidaError(f"Fecha irreconocible: {fecha_cruda!r}")

    zona = ZoneInfo(_ZONA_HORARIA_POR_LIGA[liga])
    hora, minuto = _HORA_KICKOFF_CONVENCIONAL
    kickoff_local = fecha.replace(hour=hora, minute=minuto, tzinfo=zona)
    return kickoff_local.astimezone(UTC)


def parsear_fila(fila: dict[str, str], liga: Liga) -> RegistroPartido:
    """Parsea una fila cruda de un CSV de Football-Data.co.uk a un `RegistroPartido`."""
    try:
        return RegistroPartido(
            fecha_kickoff=_parsear_fecha(fila["Date"], liga),
            equipo_local_raw=fila["HomeTeam"],
            equipo_visitante_raw=fila["AwayTeam"],
            goles_local=int(fila["FTHG"]),
            goles_visitante=int(fila["FTAG"]),
        )
    except KeyError as error:
        raise FilaPartidoInvalidaError(f"Falta la columna {error} en la fila") from error


def cargar_partidos_csv(ruta_csv: PathLike[str] | str, liga: Liga) -> list[RegistroPartido]:
    """Lee un CSV completo de Football-Data.co.uk y devuelve sus registros parseados."""
    with Path(ruta_csv).open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        return [parsear_fila(fila, liga) for fila in lector]
