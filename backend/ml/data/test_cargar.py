"""Contrato de `ml.data.cargar` — Paso 2 de la defensa EC1: llevar un CSV de
Football-Data.co.uk a Postgres para que `ml.evaluation.baseline_demo` tenga datos.

Encadena lo que ya existe (`ml.data.loader.parsear_fila`, `ml.data.alias`,
`ml.data.persist.persistir_partido`) con dos políticas explícitas para filas malas:

- Fila con goles vacíos o fecha irreconocible (partido pospuesto en Football-Data):
  se omite y se reporta con su número de línea — no se puede entrenar con ella.
- Nombre de equipo sin alias: aborta la carga completa **antes de escribir nada** y
  lista todos los alias faltantes de una vez (ml-design.md §1: nunca se adivina un
  equipo, quien carga agrega el alias a mano).

Además es idempotente: correrlo dos veces con el mismo CSV no duplica partidos, para
poder repetir la demo en vivo sin limpiar la base.

Integración contra Postgres real (Artículo IX, `db_session` de `backend/conftest.py`).

Fase Red (Artículo III): `ml.data.cargar` todavía no existe.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import func, select

from app.models.equipo import Equipo
from app.models.partido import Liga, Partido

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration

_ENCABEZADO = "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,B365H,B365D,B365A"

_TABLA_ALIAS = {
    ("Man United", "premier_league"): "manchester-united",
    ("Fulham", "premier_league"): "fulham",
    ("Arsenal", "premier_league"): "arsenal",
}


def _escribir_csv(tmp_path: Path, filas: list[str]) -> Path:
    ruta = tmp_path / "partidos.csv"
    ruta.write_text("\n".join([_ENCABEZADO, *filas]) + "\n", encoding="utf-8")
    return ruta


async def _contar(db_session: AsyncSession, modelo: type) -> int:
    """Conteo total; los tests comparan contra la cuenta previa porque la base local
    puede tener ya partidos de una demo (el `db_session` solo revierte lo del test)."""
    return (await db_session.execute(select(func.count()).select_from(modelo))).scalar_one()


async def test_carga_todas_las_filas_validas(db_session: AsyncSession, tmp_path: Path) -> None:
    from ml.data.cargar import cargar_csv_a_base

    partidos_antes = await _contar(db_session, Partido)

    ruta = _escribir_csv(
        tmp_path,
        [
            "16/08/2019,Man United,Fulham,1,0,H,1.60,4.20,5.50",
            "17/08/2019,Arsenal,Man United,2,2,D,1.90,3.60,4.00",
        ],
    )

    resultado = await cargar_csv_a_base(db_session, ruta, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    assert resultado.persistidos == 2
    assert resultado.duplicados == 0
    assert resultado.filas_omitidas == []
    assert await _contar(db_session, Partido) - partidos_antes == 2


async def test_omite_y_reporta_filas_con_goles_vacios_o_fecha_rota(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    from ml.data.cargar import cargar_csv_a_base

    partidos_antes = await _contar(db_session, Partido)

    ruta = _escribir_csv(
        tmp_path,
        [
            "16/08/2019,Man United,Fulham,1,0,H,1.60,4.20,5.50",  # línea 2: válida
            "17/08/2019,Arsenal,Fulham,,,,1.50,4.00,6.00",  # línea 3: pospuesto
            "sin-fecha,Arsenal,Man United,2,1,H,1.90,3.60,4.00",  # línea 4: fecha rota
        ],
    )

    resultado = await cargar_csv_a_base(db_session, ruta, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    assert resultado.persistidos == 1
    # Número de línea del CSV (el encabezado es la línea 1) + motivo legible.
    assert [linea for linea, _motivo in resultado.filas_omitidas] == [3, 4]
    assert all(motivo for _linea, motivo in resultado.filas_omitidas)
    assert await _contar(db_session, Partido) - partidos_antes == 1


async def test_alias_desconocido_aborta_sin_escribir_y_lista_todos_los_faltantes(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    from ml.data.cargar import AliasFaltantesError, cargar_csv_a_base

    partidos_antes = await _contar(db_session, Partido)
    equipos_antes = await _contar(db_session, Equipo)

    ruta = _escribir_csv(
        tmp_path,
        [
            # La primera fila es válida: aun así no debe quedar escrita.
            "16/08/2019,Man United,Fulham,1,0,H,1.60,4.20,5.50",
            "17/08/2019,Manchester Utd,Arsenal,0,2,A,2.10,3.40,3.30",
            "18/08/2019,Chelsea,Manchester Utd,1,1,D,2.00,3.50,3.60",
        ],
    )

    with pytest.raises(AliasFaltantesError) as error:
        await cargar_csv_a_base(db_session, ruta, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    # Todos los faltantes de una vez, sin repetir, para arreglar el CSV de alias
    # en una sola pasada.
    assert error.value.nombres_faltantes == ["Chelsea", "Manchester Utd"]
    assert await _contar(db_session, Partido) - partidos_antes == 0
    assert await _contar(db_session, Equipo) - equipos_antes == 0


async def test_cargar_dos_veces_el_mismo_csv_no_duplica_partidos(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    from ml.data.cargar import cargar_csv_a_base

    partidos_antes = await _contar(db_session, Partido)

    ruta = _escribir_csv(
        tmp_path,
        [
            "16/08/2019,Man United,Fulham,1,0,H,1.60,4.20,5.50",
            "17/08/2019,Arsenal,Man United,2,2,D,1.90,3.60,4.00",
        ],
    )

    await cargar_csv_a_base(db_session, ruta, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)
    segunda = await cargar_csv_a_base(db_session, ruta, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    assert segunda.persistidos == 0
    assert segunda.duplicados == 2
    assert await _contar(db_session, Partido) - partidos_antes == 2
