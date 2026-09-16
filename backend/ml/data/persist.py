"""Escritura de Partido/Equipo históricos (ml-design.md §1 y §2, cierre de T012b).

Combina `ml.data.loader` (parseo del CSV) y `ml.data.alias` (resolución de nombres)
para escribir el histórico en Postgres: encuentra o crea cada `Equipo` por
`(nombre, liga)` sin duplicar nunca, y crea el `Partido` correspondiente.

Ver `test_persist.py` para el contrato completo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido
from ml.data.alias import resolver_alias

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from ml.data.loader import RegistroPartido


async def buscar_o_crear_equipo(session: AsyncSession, nombre: str, liga: Liga) -> Equipo:
    """Encuentra el `Equipo` por `(nombre, liga)` o lo crea — nunca duplica.

    Protege el mismo `unique(nombre, liga)` que `ml.data.alias` señala en su docstring
    (ml-design.md §1).
    """
    resultado = await session.execute(
        select(Equipo).where(Equipo.nombre == nombre, Equipo.liga == liga)
    )
    equipo = resultado.scalar_one_or_none()
    if equipo is not None:
        return equipo

    equipo = Equipo(nombre=nombre, liga=liga)
    session.add(equipo)
    await session.flush()
    return equipo


async def persistir_partido(
    session: AsyncSession,
    registro: RegistroPartido,
    liga: Liga,
    tabla_alias: dict[tuple[str, str], str],
) -> Partido:
    """Resuelve los alias de un `RegistroPartido` y escribe `Partido`/`Equipo`.

    Si algún nombre no tiene alias registrado, `resolver_alias` propaga
    `AliasDesconocidoError` antes de tocar la sesión — no se crea ningún `Equipo`
    a medias.
    """
    nombre_local = resolver_alias(registro.equipo_local_raw, liga.value, tabla_alias)
    nombre_visitante = resolver_alias(registro.equipo_visitante_raw, liga.value, tabla_alias)

    equipo_local = await buscar_o_crear_equipo(session, nombre_local, liga)
    equipo_visitante = await buscar_o_crear_equipo(session, nombre_visitante, liga)

    partido = Partido(
        liga=liga,
        equipo_local_id=equipo_local.id,
        equipo_visitante_id=equipo_visitante.id,
        fecha_kickoff=registro.fecha_kickoff,
        estado=EstadoPartido.JUGADO,
        goles_local=registro.goles_local,
        goles_visitante=registro.goles_visitante,
    )
    session.add(partido)
    await session.flush()
    return partido
