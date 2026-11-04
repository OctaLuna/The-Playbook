"""Carga de un CSV de Football-Data.co.uk a Postgres — Paso 2 de la defensa EC1.

Deja en la base los partidos que `ml.evaluation.baseline_demo` entrena y evalúa.
Encadena `ml.data.loader.parsear_fila`, `ml.data.alias` y
`ml.data.persist.persistir_partido` con dos políticas para filas malas (ver
`test_cargar.py` para el contrato completo):

- Goles vacíos o fecha irreconocible (partido pospuesto): se omite y se reporta.
- Nombre de equipo sin alias: aborta antes de escribir nada y lista todos los
  faltantes (ml-design.md §1 — quien carga agrega el alias a mano).

Idempotente: un partido ya cargado (misma liga, equipos y kickoff) no se duplica.

Uso en vivo (día de la defensa), desde `backend/`, con Postgres arriba:

    python -m ml.data.cargar ml/data/raw/premier_league_2024.csv premier_league

El tercer argumento opcional es la ruta del CSV de alias (por defecto
`ml/data/equipo_alias.csv`).
"""

from __future__ import annotations

import asyncio
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.partido import Liga, Partido
from ml.data.alias import cargar_tabla_alias, resolver_alias
from ml.data.loader import FilaPartidoInvalidaError, parsear_fila
from ml.data.persist import buscar_o_crear_equipo, persistir_partido

if TYPE_CHECKING:
    from os import PathLike

    from sqlalchemy.ext.asyncio import AsyncSession

    from ml.data.loader import RegistroPartido

_RUTA_ALIAS_DEFAULT = Path(__file__).parent / "equipo_alias.csv"


class AliasFaltantesError(ValueError):
    """Uno o más nombres del CSV no tienen alias para la liga — no se escribió nada."""

    def __init__(self, nombres_faltantes: list[str], liga: str) -> None:
        self.nombres_faltantes = nombres_faltantes
        super().__init__(
            f"Sin alias registrado en la liga {liga!r} para: {', '.join(nombres_faltantes)}. "
            "Agregá una fila por nombre al CSV de alias y volvé a correr la carga."
        )


@dataclass
class ResultadoCarga:
    persistidos: int = 0
    duplicados: int = 0
    # (línea del CSV, motivo) — el encabezado es la línea 1.
    filas_omitidas: list[tuple[int, str]] = field(default_factory=list)


def _leer_registros(
    ruta_csv: PathLike[str] | str, liga: Liga
) -> tuple[list[RegistroPartido], list[tuple[int, str]]]:
    registros = []
    omitidas = []
    with Path(ruta_csv).open(encoding="utf-8", newline="") as archivo:
        for linea, fila in enumerate(csv.DictReader(archivo), start=2):
            try:
                registros.append(parsear_fila(fila, liga))
            except FilaPartidoInvalidaError as error:
                omitidas.append((linea, str(error)))
    return registros, omitidas


async def _ya_existe(
    session: AsyncSession,
    liga: Liga,
    registro: RegistroPartido,
    tabla_alias: dict[tuple[str, str], str],
) -> bool:
    local = await buscar_o_crear_equipo(
        session, resolver_alias(registro.equipo_local_raw, liga.value, tabla_alias), liga
    )
    visitante = await buscar_o_crear_equipo(
        session, resolver_alias(registro.equipo_visitante_raw, liga.value, tabla_alias), liga
    )
    resultado = await session.execute(
        select(Partido.id).where(
            Partido.liga == liga,
            Partido.equipo_local_id == local.id,
            Partido.equipo_visitante_id == visitante.id,
            Partido.fecha_kickoff == registro.fecha_kickoff,
        )
    )
    return resultado.first() is not None


async def cargar_csv_a_base(
    session: AsyncSession,
    ruta_csv: PathLike[str] | str,
    liga: Liga,
    tabla_alias: dict[tuple[str, str], str],
) -> ResultadoCarga:
    """Persiste los partidos válidos del CSV en `session` (sin comitear)."""
    registros, omitidas = _leer_registros(ruta_csv, liga)

    # Validar todos los alias antes de tocar la sesión: o se carga el CSV entero
    # (salvo filas omitidas) o no se escribe nada.
    nombres = {r.equipo_local_raw for r in registros} | {r.equipo_visitante_raw for r in registros}
    faltantes = sorted(n for n in nombres if (n, liga.value) not in tabla_alias)
    if faltantes:
        raise AliasFaltantesError(faltantes, liga.value)

    resultado = ResultadoCarga(filas_omitidas=omitidas)
    for registro in registros:
        if await _ya_existe(session, liga, registro, tabla_alias):
            resultado.duplicados += 1
            continue
        await persistir_partido(session, registro, liga, tabla_alias)
        resultado.persistidos += 1
    return resultado


async def main(ruta_csv: str, liga_valor: str, ruta_alias: Path) -> int:
    liga = Liga(liga_valor)
    tabla_alias = cargar_tabla_alias(ruta_alias)
    async with async_session_factory() as session:
        try:
            resultado = await cargar_csv_a_base(session, ruta_csv, liga, tabla_alias)
        except AliasFaltantesError as error:
            print(f"Carga abortada, no se escribió nada.\n{error}")
            return 1
        await session.commit()

    print(
        f"{resultado.persistidos} partidos nuevos, {resultado.duplicados} ya estaban, "
        f"{len(resultado.filas_omitidas)} filas omitidas."
    )
    for linea, motivo in resultado.filas_omitidas:
        print(f"  línea {linea}: {motivo}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python -m ml.data.cargar <csv> <liga> [csv_alias]")
        sys.exit(2)
    alias = Path(sys.argv[3]) if len(sys.argv) > 3 else _RUTA_ALIAS_DEFAULT
    sys.exit(asyncio.run(main(sys.argv[1], sys.argv[2], alias)))
