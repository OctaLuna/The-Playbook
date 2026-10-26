from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido
from ml.data.demo_fixture import crear_o_reutilizar_fixture, planificar_fixture_demo

pytestmark = pytest.mark.integration


async def test_demo_fixture_is_programmed_without_result_and_reuses_its_id(
    db_session: AsyncSession,
) -> None:
    teams = [
        Equipo(
            nombre=f"Demo team {index}-{datetime.now(UTC).timestamp()}", liga=Liga.PREMIER_LEAGUE
        )
        for index in range(4)
    ]
    db_session.add_all(teams)
    await db_session.flush()
    scores = [(2, 0), (0, 0), (0, 1), (3, 2), (1, 2)]
    start = datetime(2025, 1, 1, tzinfo=UTC)
    history = [
        Partido(
            liga=Liga.PREMIER_LEAGUE,
            equipo_local_id=teams[index % 4].id,
            equipo_visitante_id=teams[(index + 1) % 4].id,
            fecha_kickoff=start + timedelta(days=index),
            estado=EstadoPartido.JUGADO,
            goles_local=scores[index % len(scores)][0],
            goles_visitante=scores[index % len(scores)][1],
        )
        for index in range(40)
    ]
    db_session.add_all(history)
    await db_session.flush()
    now = datetime(2026, 10, 26, 12, tzinfo=UTC)
    plan = planificar_fixture_demo(history, teams, ahora=now)

    fixture, created = await crear_o_reutilizar_fixture(db_session, plan)
    again, created_again = await crear_o_reutilizar_fixture(db_session, plan)
    count = await db_session.scalar(
        select(func.count()).select_from(Partido).where(Partido.id == plan.match_id)
    )

    assert created is True
    assert created_again is False
    assert fixture.id == again.id == plan.match_id
    assert fixture.estado == EstadoPartido.PROGRAMADO
    assert fixture.fecha_kickoff == now + timedelta(hours=12)
    assert fixture.goles_local is None
    assert fixture.goles_visitante is None
    assert count == 1
