"""Resolución de nombres de equipo vía tabla de alias.

Ver ml-design.md §1 y `test_alias.py` para el contrato completo.
"""

from __future__ import annotations

import csv
from pathlib import Path


class AliasDesconocidoError(ValueError):
    """Un nombre crudo no tiene alias registrado para esa liga.

    Nunca se crea un `Equipo` nuevo en silencio ante un nombre no reconocido
    (ml-design.md §1) — quien cargue los datos agrega el alias a mano.
    """

    def __init__(self, nombre_crudo: str, liga: str) -> None:
        super().__init__(
            f"Sin alias registrado para {nombre_crudo!r} en la liga {liga!r}. "
            "Agregá una fila a equipo_alias.csv en vez de dejar que el loader "
            "adivine el equipo."
        )


def resolver_alias(nombre_crudo: str, liga: str, tabla: dict[tuple[str, str], str]) -> str:
    """Resuelve un nombre crudo de una fuente a su `equipo_id` estable.

    La clave de resolución es `(nombre_crudo, liga)`, no solo el nombre: el
    mismo nombre puede ser dos `Equipo` distintos en dos ligas distintas
    (`unique(nombre, liga)` de data-model.md).
    """
    clave = (nombre_crudo, liga)
    if clave not in tabla:
        raise AliasDesconocidoError(nombre_crudo, liga)
    return tabla[clave]


def cargar_tabla_alias(ruta_csv: Path) -> dict[tuple[str, str], str]:
    """Carga `equipo_alias.csv` (columnas: alias, equipo_id, liga) a memoria."""
    with ruta_csv.open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        return {(fila["alias"], fila["liga"]): fila["equipo_id"] for fila in lector}
