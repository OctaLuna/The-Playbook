"""Functional check for chronological model training and SHAP prediction output."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.partido import EstadoPartido
from ml.ensemble.generate import entrenar_y_predecir


def test_entrenar_y_predecir_retorna_mercados_xg_y_shap() -> None:
    teams = [uuid4() for _ in range(4)]
    start = datetime(2025, 1, 1, tzinfo=UTC)
    historical = []
    for index in range(60):
        home_index = index % len(teams)
        away_index = (home_index + 1) % len(teams)
        result = index % 3
        goals = ((3, 0), (1, 1), (0, 4))[result]
        historical.append(
            SimpleNamespace(
                id=uuid4(),
                estado=EstadoPartido.JUGADO,
                goles_local=goals[0],
                goles_visitante=goals[1],
                fecha_kickoff=start + timedelta(days=index),
                equipo_local_id=teams[home_index],
                equipo_visitante_id=teams[away_index],
            )
        )
    target = SimpleNamespace(
        id=uuid4(),
        estado=EstadoPartido.PROGRAMADO,
        goles_local=None,
        goles_visitante=None,
        fecha_kickoff=start + timedelta(days=61),
        equipo_local_id=teams[0],
        equipo_visitante_id=teams[1],
    )

    result = entrenar_y_predecir(historical, [target])[target.id]

    assert sum(
        result[key] for key in ("prob_local", "prob_empate", "prob_visitante")
    ) == pytest.approx(1.0)
    assert 0 <= result["prob_over_2_5"] <= 1
    assert 0 <= result["prob_btts_si"] <= 1
    assert result["xg_local"] > 0
    assert result["xg_visitante"] > 0
    assert result["top_shap_features"]
    assert len(result["top_shap_features"]) <= 5
    assert result["version_modelo"].startswith("ensemble-")
