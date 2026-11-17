"""La consulta de la línea base solo debe traer partidos con resultado.

Un partido programado (goles NULL) rompería las métricas de Dixon-Coles/XGBoost.
Integración contra Postgres real (Artículo IX): inserta sus propios partidos, no
depende de que el histórico del Paso 2 esté cargado.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido

pytestmark = pytest.mark.integration


async def test_consulta_excluye_partidos_sin_resultado(db_session: AsyncSession) -> None:
    from ml.evaluation.baseline_demo import _consulta_partidos_con_resultado

    local = Equipo(nombre="equipo-local-test", liga=Liga.PREMIER_LEAGUE)
    visitante = Equipo(nombre="equipo-visitante-test", liga=Liga.PREMIER_LEAGUE)
    db_session.add_all([local, visitante])
    await db_session.flush()

    jugado = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        fecha_kickoff=datetime(2024, 8, 17, 14, 0, tzinfo=UTC),
        estado=EstadoPartido.JUGADO,
        goles_local=2,
        goles_visitante=1,
    )
    programado = Partido(
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        fecha_kickoff=datetime(2030, 8, 17, 14, 0, tzinfo=UTC),
        estado=EstadoPartido.PROGRAMADO,
    )
    db_session.add_all([jugado, programado])
    await db_session.flush()

    resultado = await db_session.execute(_consulta_partidos_con_resultado(Liga.PREMIER_LEAGUE))
    ids = {p.id for p in resultado.scalars()}

    assert jugado.id in ids
    assert programado.id not in ids
