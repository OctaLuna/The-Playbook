"""Preflight and deterministic team selection for a local demo fixture."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.partido import EstadoPartido, Liga
from ml.data.demo_fixture import seleccionar_equipos_demo, validar_historico


def _matches(count: int = 40, *, outcomes: list[tuple[int, int]] | None = None):
    teams = [uuid4() for _ in range(4)]
    scores = outcomes or [(2, 0), (0, 0), (0, 1), (3, 2), (1, 2)]
    start = datetime(2025, 1, 1, tzinfo=UTC)
    return [
        SimpleNamespace(
            estado=EstadoPartido.JUGADO,
            goles_local=scores[index % len(scores)][0],
            goles_visitante=scores[index % len(scores)][1],
            fecha_kickoff=start + timedelta(days=index),
            equipo_local_id=teams[index % 4],
            equipo_visitante_id=teams[(index + 1) % 4],
        )
        for index in range(count)
    ]


def test_rejects_history_below_30_complete_matches() -> None:
    with pytest.raises(ValueError, match="30 partidos"):
        validar_historico(_matches(29))


def test_rejects_training_split_missing_a_1x2_class() -> None:
    with pytest.raises(ValueError, match="tres resultados 1X2"):
        validar_historico(_matches(40, outcomes=[(2, 0)]))


def test_selects_two_distinct_same_league_teams_with_five_train_matches() -> None:
    matches = validar_historico(_matches())
    team_ids = {match.equipo_local_id for match in matches} | {
        match.equipo_visitante_id for match in matches
    }
    teams = [
        SimpleNamespace(
            id=team_id,
            nombre=f"Team {index}",
            liga=Liga.PREMIER_LEAGUE,
        )
        for index, team_id in enumerate(sorted(team_ids, key=str))
    ]

    home, away = seleccionar_equipos_demo(matches, teams)

    assert home.id != away.id
    assert home.liga == away.liga
    for team in (home, away):
        appearances = sum(
            team.id in {match.equipo_local_id, match.equipo_visitante_id} for match in matches
        )
        assert appearances >= 5


def test_rejects_when_no_two_teams_have_enough_training_history() -> None:
    matches = _matches()
    teams = [
        SimpleNamespace(id=uuid4(), nombre=f"Team {index}", liga=Liga.PREMIER_LEAGUE)
        for index in range(5)
    ]
    with pytest.raises(ValueError, match="dos equipos"):
        seleccionar_equipos_demo(matches, teams)
