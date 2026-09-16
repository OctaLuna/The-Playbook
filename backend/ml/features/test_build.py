"""Contrato de `ml.features.build` — el feature set cerrado de XGBoost (T012c).

Ver `ml-design.md` §4: la tabla de 5 features (`forma`, `goles_favor/contra_reciente`,
`descanso_dias`, `h2h_forma`, `fuerza_relativa_ataque/defensa`) se calcula una por
equipo local/visitante, salvo `h2h_forma` que es un único valor desde la perspectiva
del local. `fuerza_relativa_*` viene de un Dixon-Coles ya entrenado — este módulo lo
recibe como parámetro (`fuerza_dixon_coles`), nunca lo entrena (Art. I: cada módulo de
`ml/models/*/` es independiente).

Cada feature usa **solo** partidos estrictamente anteriores al kickoff del partido en
cuestión — la misma disciplina de integridad temporal que `ml.evaluation.split`
(Artículo IV en espíritu, aunque el artículo en la letra habla de RAG).

Fase Red (Artículo III): `ml.features.build` todavía no existe.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.models.partido import EstadoPartido, Liga, Partido

pytestmark = pytest.mark.unit

_LOCAL = uuid4()
_VISITANTE = uuid4()
_RIVAL_HISTORICO = uuid4()
_KICKOFF = datetime(2024, 10, 1, 15, 0, tzinfo=UTC)


def _partido(
    *,
    local: UUID,
    visitante: UUID,
    dias_antes: int,
    goles_local: int,
    goles_visitante: int,
    estado: EstadoPartido = EstadoPartido.JUGADO,
) -> Partido:
    return Partido(
        id=uuid4(),
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local,
        equipo_visitante_id=visitante,
        fecha_kickoff=_KICKOFF - timedelta(days=dias_antes),
        estado=estado,
        goles_local=goles_local,
        goles_visitante=goles_visitante,
    )


def _partido_objetivo() -> Partido:
    return _partido(
        local=_LOCAL,
        visitante=_VISITANTE,
        dias_antes=0,
        goles_local=0,
        goles_visitante=0,
        estado=EstadoPartido.PROGRAMADO,
    )


def test_devuelve_un_dataframe_vacio_con_las_columnas_del_feature_set_cerrado() -> None:
    from ml.features.build import COLUMNAS_FEATURE_SET, construir_feature_set

    resultado = construir_feature_set(partidos=[])

    assert list(resultado.columns) == COLUMNAS_FEATURE_SET
    assert len(resultado) == 0


def test_una_fila_por_partido_de_entrada() -> None:
    from ml.features.build import construir_feature_set

    objetivo = _partido_objetivo()
    resultado = construir_feature_set(partidos=[objetivo])

    assert len(resultado) == 1


def test_forma_es_el_promedio_de_puntos_normalizado_de_los_ultimos_5_partidos() -> None:
    from ml.features.build import construir_feature_set

    # Local: 2 victorias y 1 empate en sus últimos 3 partidos -> (3+3+1)/3 / 3 = 7/9.
    historial_local = [
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=3, goles_local=2, goles_visitante=0),
        _partido(local=uuid4(), visitante=_LOCAL, dias_antes=6, goles_local=0, goles_visitante=1),
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=9, goles_local=1, goles_visitante=1),
    ]
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[*historial_local, objetivo])

    forma = resultado.iloc[-1]["forma_local"]
    assert forma == pytest.approx((3 + 3 + 1) / 3 / 3)


def test_forma_solo_usa_partidos_estrictamente_anteriores_al_kickoff() -> None:
    """Integridad temporal: un resultado posterior al partido objetivo no debe filtrarse."""
    from ml.features.build import construir_feature_set

    partido_futuro = _partido(
        local=_LOCAL, visitante=uuid4(), dias_antes=-3, goles_local=5, goles_visitante=0
    )
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[partido_futuro, objetivo])

    assert resultado.iloc[-1]["forma_local"] is None


def test_forma_es_none_sin_historial_previo() -> None:
    from ml.features.build import construir_feature_set

    resultado = construir_feature_set(partidos=[_partido_objetivo()])

    assert resultado.iloc[0]["forma_local"] is None
    assert resultado.iloc[0]["forma_visitante"] is None


def test_solo_toma_los_ultimos_5_partidos_aunque_haya_mas_historial() -> None:
    from ml.features.build import construir_feature_set

    # 6 derrotas seguidas y, antes de esas, una racha de victorias que NO debe contar.
    historial = [
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=d, goles_local=0, goles_visitante=1)
        for d in range(1, 6)
    ] + [
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=d, goles_local=3, goles_visitante=0)
        for d in range(10, 15)
    ]
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[*historial, objetivo])

    assert resultado.iloc[-1]["forma_local"] == pytest.approx(0.0)


def test_goles_favor_y_contra_recientes_son_el_promedio_de_los_ultimos_5() -> None:
    from ml.features.build import construir_feature_set

    historial = [
        _partido(
            local=_VISITANTE, visitante=uuid4(), dias_antes=2, goles_local=2, goles_visitante=1
        ),
        _partido(
            local=uuid4(), visitante=_VISITANTE, dias_antes=4, goles_local=0, goles_visitante=3
        ),
    ]
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[*historial, objetivo])
    fila = resultado.iloc[-1]

    assert fila["goles_favor_reciente_visitante"] == pytest.approx((2 + 3) / 2)
    assert fila["goles_contra_reciente_visitante"] == pytest.approx((1 + 0) / 2)


def test_descanso_dias_es_la_diferencia_con_el_partido_anterior_del_equipo() -> None:
    from ml.features.build import construir_feature_set

    historial = [
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=6, goles_local=1, goles_visitante=0)
    ]
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[*historial, objetivo])

    assert resultado.iloc[-1]["descanso_dias_local"] == pytest.approx(6.0)


def test_descanso_dias_es_none_sin_partido_anterior() -> None:
    from ml.features.build import construir_feature_set

    resultado = construir_feature_set(partidos=[_partido_objetivo()])

    assert resultado.iloc[0]["descanso_dias_visitante"] is None


def test_h2h_forma_es_el_promedio_normalizado_de_puntos_del_local_en_enfrentamientos_previos() -> (
    None
):
    from ml.features.build import construir_feature_set

    # El equipo local le ganó una vez y empató otra a este mismo rival.
    historial_h2h = [
        _partido(
            local=_LOCAL, visitante=_VISITANTE, dias_antes=200, goles_local=2, goles_visitante=0
        ),
        _partido(
            local=_VISITANTE, visitante=_LOCAL, dias_antes=380, goles_local=1, goles_visitante=1
        ),
    ]
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[*historial_h2h, objetivo])

    assert resultado.iloc[-1]["h2h_forma"] == pytest.approx((3 + 1) / 2 / 3)


def test_h2h_forma_ignora_partidos_contra_otros_rivales() -> None:
    from ml.features.build import construir_feature_set

    contra_otro_rival = _partido(
        local=_LOCAL, visitante=_RIVAL_HISTORICO, dias_antes=10, goles_local=5, goles_visitante=0
    )
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[contra_otro_rival, objetivo])

    assert resultado.iloc[-1]["h2h_forma"] is None


def test_fuerza_relativa_toma_alpha_beta_del_dixon_coles_recibido_por_parametro() -> None:
    from ml.features.build import construir_feature_set

    fuerza = {
        _LOCAL: (0.42, -0.10),
        _VISITANTE: (-0.05, 0.20),
    }
    objetivo = _partido_objetivo()

    resultado = construir_feature_set(partidos=[objetivo], fuerza_dixon_coles=fuerza)
    fila = resultado.iloc[0]

    assert fila["fuerza_relativa_ataque_local"] == pytest.approx(0.42)
    assert fila["fuerza_relativa_defensa_local"] == pytest.approx(-0.10)
    assert fila["fuerza_relativa_ataque_visitante"] == pytest.approx(-0.05)
    assert fila["fuerza_relativa_defensa_visitante"] == pytest.approx(0.20)


def test_fuerza_relativa_es_none_sin_dixon_coles_entrenado() -> None:
    from ml.features.build import construir_feature_set

    resultado = construir_feature_set(partidos=[_partido_objetivo()])
    fila = resultado.iloc[0]

    assert fila["fuerza_relativa_ataque_local"] is None
    assert fila["fuerza_relativa_defensa_visitante"] is None


def test_tiene_historial_suficiente_exige_al_menos_5_partidos_jugados() -> None:
    from ml.features.build import tiene_historial_suficiente

    cuatro_partidos = [
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=d, goles_local=1, goles_visitante=0)
        for d in range(1, 5)
    ]
    cinco_partidos = [
        *cuatro_partidos,
        _partido(local=_LOCAL, visitante=uuid4(), dias_antes=5, goles_local=1, goles_visitante=0),
    ]

    assert tiene_historial_suficiente(cuatro_partidos) is False
    assert tiene_historial_suficiente(cinco_partidos) is True


def test_head_to_head_disponible_exige_al_menos_un_enfrentamiento_previo() -> None:
    from ml.features.build import head_to_head_disponible

    assert head_to_head_disponible([]) is False
    assert head_to_head_disponible([_partido_objetivo()]) is True
