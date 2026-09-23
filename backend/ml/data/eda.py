"""Perfilado estadístico de los datos crudos (EDA) — evidencia para la defensa EC1.

No es parte del pipeline de entrenamiento ni de features (`ml.features.build`): existe
únicamente para responder, con datos reales, las tres preguntas de calidad de datos que
pide la rúbrica de la defensa — volumen, % de nulos e inconsistencias en nombres de
equipo. Ver `docs/scrum/Auditorias/guia-defensa-ec1.md` bloque 3 ("Datos") y
ml-design.md §1.

Demostración en vivo (día de la defensa), desde `backend/`:

    python -m ml.data.eda ml/data/raw/premier_league_2024.csv premier_league

Requiere un CSV real de Football-Data.co.uk en `ml/data/raw/` (gitignorado — no se
commitea, cada quien lo descarga localmente) y `ml/data/equipo_alias.csv` ya cargado.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ml.data.alias import AliasDesconocidoError, cargar_tabla_alias, resolver_alias

if TYPE_CHECKING:
    from os import PathLike

_COLUMNAS_REQUERIDAS = ("Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG")
_RUTA_ALIAS_DEFAULT = Path(__file__).parent / "equipo_alias.csv"


@dataclass(frozen=True)
class PerfilColumnas:
    """Volumen y huecos (`nulos`) por columna requerida de un CSV crudo, sin transformarlo."""

    total_filas: int
    nulos_por_columna: dict[str, int]

    def porcentaje_nulos(self, columna: str) -> float:
        if self.total_filas == 0:
            return 0.0
        return round(100 * self.nulos_por_columna.get(columna, 0) / self.total_filas, 2)


@dataclass(frozen=True)
class PerfilAlias:
    """Qué tan resuelto está el mapeo de nombres crudos de equipo a `equipo_id`."""

    equipos_distintos: list[str]
    equipos_sin_alias: list[str]

    @property
    def porcentaje_resuelto(self) -> float:
        if not self.equipos_distintos:
            return 100.0
        resueltos = len(self.equipos_distintos) - len(self.equipos_sin_alias)
        return round(100 * resueltos / len(self.equipos_distintos), 2)


def perfilar_columnas(ruta_csv: PathLike[str] | str) -> PerfilColumnas:
    """Cuenta filas y valores vacíos por columna requerida de un CSV crudo."""
    nulos: Counter[str] = Counter()
    total = 0
    with Path(ruta_csv).open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            total += 1
            for columna in _COLUMNAS_REQUERIDAS:
                if not fila.get(columna, "").strip():
                    nulos[columna] += 1
    return PerfilColumnas(total_filas=total, nulos_por_columna=dict(nulos))


def perfilar_alias(
    nombres_crudos: list[str], liga: str, tabla: dict[tuple[str, str], str]
) -> PerfilAlias:
    """Para cada nombre crudo único, intenta resolverlo y junta los que no tienen alias."""
    distintos = sorted(set(nombres_crudos), key=nombres_crudos.index)
    sin_alias = [nombre for nombre in distintos if _sin_alias(nombre, liga, tabla)]
    return PerfilAlias(equipos_distintos=distintos, equipos_sin_alias=sin_alias)


def _sin_alias(nombre: str, liga: str, tabla: dict[tuple[str, str], str]) -> bool:
    try:
        resolver_alias(nombre, liga, tabla)
    except AliasDesconocidoError:
        return True
    return False


def _nombres_crudos(ruta_csv: Path) -> list[str]:
    nombres: list[str] = []
    with ruta_csv.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            nombres.append(fila["HomeTeam"])
            nombres.append(fila["AwayTeam"])
    return nombres


def _imprimir_reporte(ruta_csv: Path, liga: str, ruta_alias: Path) -> None:
    """Imprime el reporte de perfilado — pensado para correrse en vivo en la defensa."""
    perfil_columnas = perfilar_columnas(ruta_csv)
    tabla_alias = cargar_tabla_alias(ruta_alias)
    perfil_alias = perfilar_alias(_nombres_crudos(ruta_csv), liga, tabla_alias)

    print(f"=== Perfilado de datos: {ruta_csv.name} (liga={liga}) ===")
    print(f"Total de filas: {perfil_columnas.total_filas}")
    print("Vacíos/nulos por columna:")
    for columna in _COLUMNAS_REQUERIDAS:
        nulos = perfil_columnas.nulos_por_columna.get(columna, 0)
        print(f"  {columna}: {nulos} ({perfil_columnas.porcentaje_nulos(columna)}%)")

    print(f"\nEquipos distintos en el CSV: {len(perfil_alias.equipos_distintos)}")
    print(f"Resueltos por equipo_alias.csv: {perfil_alias.porcentaje_resuelto}%")
    if perfil_alias.equipos_sin_alias:
        print("Sin alias registrado (agregar fila a equipo_alias.csv):")
        for nombre in perfil_alias.equipos_sin_alias:
            print(f"  - {nombre}")

    try:
        import pandas as pd

        df = pd.read_csv(ruta_csv)
        print("\n--- df.describe() de columnas numéricas (FTHG/FTAG) ---")
        print(df[["FTHG", "FTAG"]].describe())
    except ImportError:
        print("\n(pandas no disponible — se omite df.describe())")


def main(argv: list[str] | None = None) -> int:
    argumentos = sys.argv[1:] if argv is None else argv
    if len(argumentos) < 2:
        print("Uso: python -m ml.data.eda <ruta_csv> <liga> [ruta_equipo_alias.csv]")
        return 1

    ruta_csv = Path(argumentos[0])
    liga = argumentos[1]
    ruta_alias = Path(argumentos[2]) if len(argumentos) > 2 else _RUTA_ALIAS_DEFAULT

    _imprimir_reporte(ruta_csv, liga, ruta_alias)
    return 0


if __name__ == "__main__":
    sys.exit(main())
