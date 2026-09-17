"""Contrato de `ml.models.dixon_coles.train` (T012d).

Ver `ml-design.md` §3: el ajuste es una optimización del log-likelihood
negativo sobre alpha/beta/gamma/rho (scipy, Artículo VIII), con la
restricción de identificabilidad "suma de alpha = 0" y `ξ = 0.0018` como
default de configuración, no ajustado por optimización.

Los tests de "fuerza relativa" usan un round-robin sintético con una
jerarquía de resultados clara (FUERTE > MEDIO > DEBIL en cada enfrentamiento)
para verificar que el ajuste recupera esa jerarquía en alpha — no se verifica
un valor numérico exacto, porque eso depende del optimizador, solo el orden,
que es lo que el resto del sistema (features de XGBoost, badge de confianza)
efectivamente consume.

Fase Red (Artículo III): `ml.models.dixon_coles.train` todavía no existe.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.models.partido import EstadoPartido, Liga, Partido

pytestmark = pytest.mark.unit

_FUERTE = uuid4()
_MEDIO = uuid4()
_DEBIL = uuid4()
_HOY = datetime(2024, 10, 1, 15, 0, tzinfo=UTC)


def _partido(
    *, local, visitante, dias_antes, goles_local, goles_visitante, estado=EstadoPartido.JUGADO
) -> Partido:
    return Partido(
        id=uuid4(),
        liga=Liga.PREMIER_LEAGUE,
        equipo_local_id=local,
        equipo_visitante_id=visitante,
        fecha_kickoff=_HOY - timedelta(days=dias_antes),
        estado=estado,
        goles_local=goles_local,
        goles_visitante=goles_visitante,
    )


def _historial_jerarquico() -> list[Partido]:
    """Round-robin entre 3 equipos con una jerarquía de fuerza consistente
    (FUERTE > MEDIO > DEBIL) pero con variación de marcador — a propósito,
    nunca un equipo deja en blanco a su rival en *todos* sus enfrentamientos.

    Un fixture donde un equipo nunca concede (como una versión anterior de
    este archivo tenía) separa perfectamente los datos: la verosimilitud de
    Dixon-Coles es monótona en esa dirección y el MLE no converge a un punto
    finito (beta de ese equipo diverge a `-∞`), que es el comportamiento
    matemáticamente correcto del estimador, no un bug del ajuste — pero hace
    el resultado del test dependiente del criterio de parada del optimizador
    en vez de la jerarquía real. Datos reales de fútbol no tienen este
    problema porque ningún equipo mantiene el arco en cero siempre.
    """
    return [
        _partido(local=_FUERTE, visitante=_MEDIO, dias_antes=1, goles_local=2, goles_visitante=1),
        _partido(local=_MEDIO, visitante=_FUERTE, dias_antes=4, goles_local=1, goles_visitante=2),
        _partido(local=_FUERTE, visitante=_MEDIO, dias_antes=25, goles_local=1, goles_visitante=0),
        _partido(local=_MEDIO, visitante=_FUERTE, dias_antes=28, goles_local=0, goles_visitante=2),
        _partido(local=_FUERTE, visitante=_DEBIL, dias_antes=7, goles_local=3, goles_visitante=1),
        _partido(local=_DEBIL, visitante=_FUERTE, dias_antes=10, goles_local=0, goles_visitante=2),
        _partido(local=_FUERTE, visitante=_DEBIL, dias_antes=31, goles_local=1, goles_visitante=0),
        _partido(local=_DEBIL, visitante=_FUERTE, dias_antes=34, goles_local=1, goles_visitante=3),
        _partido(local=_MEDIO, visitante=_DEBIL, dias_antes=13, goles_local=2, goles_visitante=1),
        _partido(local=_DEBIL, visitante=_MEDIO, dias_antes=16, goles_local=1, goles_visitante=2),
        _partido(local=_MEDIO, visitante=_DEBIL, dias_antes=37, goles_local=1, goles_visitante=1),
        _partido(local=_DEBIL, visitante=_MEDIO, dias_antes=40, goles_local=0, goles_visitante=2),
    ]


def test_no_hay_partidos_jugados_falla_explicito() -> None:
    from ml.models.dixon_coles.train import entrenar_dixon_coles

    solo_programado = [
        _partido(
            local=_FUERTE,
            visitante=_MEDIO,
            dias_antes=0,
            goles_local=0,
            goles_visitante=0,
            estado=EstadoPartido.PROGRAMADO,
        )
    ]

    with pytest.raises(ValueError, match="No hay partidos"):
        entrenar_dixon_coles(solo_programado)


def test_usa_xi_0_0018_por_default() -> None:
    from ml.models.dixon_coles.train import XI_DEFAULT, entrenar_dixon_coles

    assert pytest.approx(0.0018) == XI_DEFAULT

    parametros = entrenar_dixon_coles(_historial_jerarquico())

    assert parametros.xi == pytest.approx(0.0018)


def test_respeta_la_restriccion_de_identificabilidad_suma_alpha_cero() -> None:
    from ml.models.dixon_coles.train import entrenar_dixon_coles

    parametros = entrenar_dixon_coles(_historial_jerarquico())

    assert sum(parametros.alpha.values()) == pytest.approx(0.0, abs=1e-6)


def test_devuelve_alpha_y_beta_para_cada_equipo_que_jugo() -> None:
    from ml.models.dixon_coles.train import entrenar_dixon_coles

    parametros = entrenar_dixon_coles(_historial_jerarquico())

    assert set(parametros.alpha) == {_FUERTE, _MEDIO, _DEBIL}
    assert set(parametros.beta) == {_FUERTE, _MEDIO, _DEBIL}


def test_recupera_la_jerarquia_de_fuerza_de_ataque_en_alpha() -> None:
    """El equipo que domina todos sus enfrentamientos debe terminar con un
    alpha (fuerza de ataque) más alto que uno intermedio, y ese más alto que
    el que pierde todo — la propiedad que consume `fuerza_relativa_ataque`
    de `ml.features.build` (T012c)."""
    from ml.models.dixon_coles.train import entrenar_dixon_coles

    parametros = entrenar_dixon_coles(_historial_jerarquico())

    assert parametros.alpha[_FUERTE] > parametros.alpha[_MEDIO] > parametros.alpha[_DEBIL]


def test_recupera_la_jerarquia_de_fuerza_defensiva_en_beta() -> None:
    """beta es fuerza de defensa: menor beta = defensa más sólida (`μ`/`λ`
    del rival caen con beta más chico). El equipo con la defensa más sólida
    del historial sintético debe terminar con el beta más bajo."""
    from ml.models.dixon_coles.train import entrenar_dixon_coles

    parametros = entrenar_dixon_coles(_historial_jerarquico())

    assert parametros.beta[_FUERTE] < parametros.beta[_MEDIO] < parametros.beta[_DEBIL]
