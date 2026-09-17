"""Contrato de `ml.models.dixon_coles.predict` (T012d).

Ver `ml-design.md` §3: `λ`/`μ` son las tasas de gol esperadas del local/visitante
(`exp(alpha_i + beta_j + gamma)` / `exp(alpha_j + beta_i)`), y son exactamente `xg_local`/
`xg_visitante` de `Predicción` — no un xG a nivel de tiro. La matriz de
probabilidad de marcador es Poisson bivariada con la corrección `τ` del paper
original, aplicada solo cuando ambos marcadores son `≤ 1`. 1X2, Over/Under 2.5
y BTTS salen de sumar esa misma matriz sobre los rangos correspondientes — no
hay fórmula cerrada separada por mercado.

`ParametrosDixonColes` se construye acá a mano (sin pasar por `train.py`) para
que este contrato sea independiente del ajuste por máxima verosimilitud —
`test_train.py` cubre eso.

Fase Red (Artículo III): `ml.models.dixon_coles.predict` todavía no existe.
"""

from __future__ import annotations

from math import exp
from uuid import uuid4

import pytest
from scipy.stats import poisson

pytestmark = pytest.mark.unit

_LOCAL = uuid4()
_VISITANTE = uuid4()


def _parametros(*, alpha, beta, gamma=0.0, rho=0.0):
    from ml.models.dixon_coles.train import ParametrosDixonColes

    return ParametrosDixonColes(alpha=alpha, beta=beta, gamma=gamma, rho=rho, xi=0.0018)


class TestTauDixonColes:
    def test_corrige_el_marcador_0_0(self) -> None:
        from ml.models.dixon_coles.predict import tau_dixon_coles

        assert tau_dixon_coles(0, 0, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(
            1 - 1.2 * 0.8 * 0.05
        )

    def test_corrige_el_marcador_0_1(self) -> None:
        from ml.models.dixon_coles.predict import tau_dixon_coles

        assert tau_dixon_coles(0, 1, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1 + 1.2 * 0.05)

    def test_corrige_el_marcador_1_0(self) -> None:
        from ml.models.dixon_coles.predict import tau_dixon_coles

        assert tau_dixon_coles(1, 0, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1 + 0.8 * 0.05)

    def test_corrige_el_marcador_1_1(self) -> None:
        from ml.models.dixon_coles.predict import tau_dixon_coles

        assert tau_dixon_coles(1, 1, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1 - 0.05)

    def test_no_corrige_marcadores_fuera_de_los_4_casos_bajos(self) -> None:
        from ml.models.dixon_coles.predict import tau_dixon_coles

        assert tau_dixon_coles(2, 0, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1.0)
        assert tau_dixon_coles(0, 2, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1.0)
        assert tau_dixon_coles(3, 3, lam=1.2, mu=0.8, rho=0.05) == pytest.approx(1.0)


class TestTasasEsperadas:
    def test_lambda_es_exp_alpha_local_mas_beta_visitante_mas_gamma(self) -> None:
        from ml.models.dixon_coles.predict import tasas_esperadas

        parametros = _parametros(
            alpha={_LOCAL: 0.4, _VISITANTE: -0.1},
            beta={_LOCAL: -0.2, _VISITANTE: 0.3},
            gamma=0.25,
        )

        lam, _ = tasas_esperadas(parametros, _LOCAL, _VISITANTE)

        assert lam == pytest.approx(exp(0.4 + 0.3 + 0.25))

    def test_mu_es_exp_alpha_visitante_mas_beta_local(self) -> None:
        from ml.models.dixon_coles.predict import tasas_esperadas

        parametros = _parametros(
            alpha={_LOCAL: 0.4, _VISITANTE: -0.1},
            beta={_LOCAL: -0.2, _VISITANTE: 0.3},
            gamma=0.25,
        )

        _, mu = tasas_esperadas(parametros, _LOCAL, _VISITANTE)

        assert mu == pytest.approx(exp(-0.1 + -0.2))


class TestMatrizProbabilidadMarcador:
    def test_la_matriz_suma_aproximadamente_1(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador

        matriz = matriz_probabilidad_marcador(lam=1.4, mu=1.1, rho=0.05)

        assert matriz.sum() == pytest.approx(1.0, abs=1e-6)

    def test_una_celda_baja_incluye_la_correccion_tau(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, tau_dixon_coles

        lam, mu, rho = 1.4, 1.1, 0.05
        matriz = matriz_probabilidad_marcador(lam=lam, mu=mu, rho=rho)

        # Antes de renormalizar, la celda (0,0) lleva la corrección τ. La
        # matriz sale renormalizada para sumar 1 (docstring de
        # `matriz_probabilidad_marcador`), así que se compara la *razón*
        # contra una celda sin corrección — invariante a ese reescalado — en
        # vez del valor absoluto crudo de Poisson.
        crudo_0_0 = poisson.pmf(0, lam) * poisson.pmf(0, mu) * tau_dixon_coles(0, 0, lam, mu, rho)
        crudo_2_2 = poisson.pmf(2, lam) * poisson.pmf(2, mu)
        assert matriz[0, 0] / matriz[2, 2] == pytest.approx(crudo_0_0 / crudo_2_2)

    def test_una_celda_fuera_del_rango_bajo_no_lleva_correccion(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador

        lam, mu = 1.4, 1.1
        matriz = matriz_probabilidad_marcador(lam=lam, mu=mu, rho=0.05)

        crudo_2_3 = poisson.pmf(2, lam) * poisson.pmf(3, mu)
        crudo_2_2 = poisson.pmf(2, lam) * poisson.pmf(2, mu)
        assert matriz[2, 3] / matriz[2, 2] == pytest.approx(crudo_2_3 / crudo_2_2)


class TestProbabilidad1X2:
    def test_las_tres_probabilidades_suman_1(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, probabilidad_1x2

        matriz = matriz_probabilidad_marcador(lam=1.4, mu=1.1, rho=0.05)
        prob = probabilidad_1x2(matriz)

        assert prob["local"] + prob["empate"] + prob["visitante"] == pytest.approx(1.0, abs=1e-6)

    def test_un_local_mucho_mas_fuerte_tiene_mayor_probabilidad_de_ganar(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, probabilidad_1x2

        matriz = matriz_probabilidad_marcador(lam=2.6, mu=0.5, rho=0.0)
        prob = probabilidad_1x2(matriz)

        assert prob["local"] > prob["visitante"]
        assert prob["local"] > prob["empate"]


class TestProbabilidadOverUnder25:
    def test_over_y_under_suman_1(self) -> None:
        from ml.models.dixon_coles.predict import (
            matriz_probabilidad_marcador,
            probabilidad_over_under_2_5,
        )

        matriz = matriz_probabilidad_marcador(lam=1.4, mu=1.1, rho=0.05)
        prob = probabilidad_over_under_2_5(matriz)

        assert prob["over"] + prob["under"] == pytest.approx(1.0, abs=1e-6)

    def test_tasas_de_gol_altas_favorecen_el_over(self) -> None:
        from ml.models.dixon_coles.predict import (
            matriz_probabilidad_marcador,
            probabilidad_over_under_2_5,
        )

        matriz_alta = matriz_probabilidad_marcador(lam=2.5, mu=2.0, rho=0.0)
        matriz_baja = matriz_probabilidad_marcador(lam=0.5, mu=0.4, rho=0.0)

        assert (
            probabilidad_over_under_2_5(matriz_alta)["over"]
            > probabilidad_over_under_2_5(matriz_baja)["over"]
        )


class TestProbabilidadBtts:
    def test_si_y_no_suman_1(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, probabilidad_btts

        matriz = matriz_probabilidad_marcador(lam=1.4, mu=1.1, rho=0.05)
        prob = probabilidad_btts(matriz)

        assert prob["si"] + prob["no"] == pytest.approx(1.0, abs=1e-6)

    def test_dos_ataques_fuertes_favorecen_que_ambos_marquen(self) -> None:
        from ml.models.dixon_coles.predict import matriz_probabilidad_marcador, probabilidad_btts

        matriz_ofensiva = matriz_probabilidad_marcador(lam=2.2, mu=1.8, rho=0.0)
        matriz_defensiva = matriz_probabilidad_marcador(lam=0.3, mu=0.2, rho=0.0)

        assert probabilidad_btts(matriz_ofensiva)["si"] > probabilidad_btts(matriz_defensiva)["si"]
