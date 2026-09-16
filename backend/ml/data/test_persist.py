"""Contrato de `ml.data.persist` — escritura de Partido/Equipo históricos.

Cierra el T012b de `specs/001-prediccion-partido/tasks.md`: `ml.data.alias` (ya
implementado) resuelve el nombre crudo del CSV a un identificador estable;
`ml.data.persist` lo usa para encontrar o crear el `Equipo` (ml-design.md §1:
"nunca crea un Equipo duplicado en silencio") y escribir el `Partido` histórico.

Integración contra Postgres real (Artículo IX, `db_session` de `backend/conftest.py`),
nunca un mock de la sesión — es exactamente el tipo de invariante (unicidad por
`(nombre, liga)`) que un mock no puede verificar de verdad.

Fase Red (Artículo III): `ml.data.persist` todavía no existe.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga

pytestmark = pytest.mark.integration

_TABLA_ALIAS = {
    ("Man United", "premier_league"): "manchester-united",
    ("Fulham", "premier_league"): "fulham",
}


def _registro(**overrides):
    from ml.data.loader import RegistroPartido

    base = {
        "fecha_kickoff": datetime(2024, 8, 17, 14, 0, tzinfo=UTC),
        "equipo_local_raw": "Man United",
        "equipo_visitante_raw": "Fulham",
        "goles_local": 1,
        "goles_visitante": 0,
    }
    base.update(overrides)
    return RegistroPartido(**base)


async def test_persistir_partido_crea_los_dos_equipos_nuevos(db_session: AsyncSession) -> None:
    from ml.data.persist import persistir_partido

    await persistir_partido(db_session, _registro(), Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    equipos = (
        (await db_session.execute(select(Equipo).where(Equipo.liga == Liga.PREMIER_LEAGUE)))
        .scalars()
        .all()
    )
    nombres = {e.nombre for e in equipos}
    assert nombres == {"manchester-united", "fulham"}


async def test_persistir_partido_no_duplica_un_equipo_ya_existente(
    db_session: AsyncSession,
) -> None:
    from ml.data.persist import persistir_partido

    await persistir_partido(db_session, _registro(), Liga.PREMIER_LEAGUE, _TABLA_ALIAS)
    # Mismo equipo local, rival distinto en la misma liga — no debe crear un segundo
    # "manchester-united".
    otro_registro = _registro(equipo_visitante_raw="Fulham", goles_local=2, goles_visitante=2)
    await persistir_partido(db_session, otro_registro, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    equipos = (
        (
            await db_session.execute(
                select(Equipo).where(
                    Equipo.nombre == "manchester-united", Equipo.liga == Liga.PREMIER_LEAGUE
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(equipos) == 1


async def test_persistir_partido_escribe_goles_y_estado_jugado(db_session: AsyncSession) -> None:
    from ml.data.persist import persistir_partido

    partido = await persistir_partido(db_session, _registro(), Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    assert partido.estado == EstadoPartido.JUGADO
    assert partido.goles_local == 1
    assert partido.goles_visitante == 0
    assert partido.fecha_kickoff == datetime(2024, 8, 17, 14, 0, tzinfo=UTC)


async def test_persistir_partido_propaga_alias_desconocido_sin_crear_equipo(
    db_session: AsyncSession,
) -> None:
    from ml.data.alias import AliasDesconocidoError
    from ml.data.persist import persistir_partido

    registro = _registro(equipo_local_raw="Nottingham Forest")

    with pytest.raises(AliasDesconocidoError):
        await persistir_partido(db_session, registro, Liga.PREMIER_LEAGUE, _TABLA_ALIAS)

    equipos = (
        (await db_session.execute(select(Equipo).where(Equipo.liga == Liga.PREMIER_LEAGUE)))
        .scalars()
        .all()
    )
    assert equipos == []
