"""Contrato de `ml.evaluation.calibration` (T013).

Ver `ml-design.md` §6 y `docs/adr/0001-badge-confianza-calibrado.md`: el
nivel de confianza SIEMPRE sale de la precisión histórica observada por
bucket de probabilidad predicha — nunca de la distancia a un reparto
uniforme.

1. Ordenar las predicciones de validación por la probabilidad predicha del
   resultado más probable, agrupadas en buckets de ancho 0.1 sobre
   `[0.33, 1.0]` para 1X2 y `[0.5, 1.0]` para los mercados binarios.
2. `precision_empirica = aciertos_del_bucket / n_observaciones_del_bucket`.
3. Mapeo a badge: `≥0.60` Alta, `[0.45,0.60)` Media, `<0.45` Baja.
4. `n_observaciones < 30` (default) → Baja sin mirar `precision_empirica`.

Estas pruebas viven en `backend/tests/unit/` por instrucción explícita del
"Orden de creación de archivos" de `plan.md` ("...y de la asignación de
badge de confianza").

Fase Red (Artículo III): `ml.evaluation.calibration` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestBuckets:
    def test_buckets_1x2_van_de_033_a_1_en_pasos_de_01(self) -> None:
        from ml.evaluation.calibration import BUCKETS_1X2

        assert BUCKETS_1X2 == (
            (0.33, 0.43),
            (0.43, 0.53),
            (0.53, 0.63),
            (0.63, 0.73),
            (0.73, 0.83),
            (0.83, 0.93),
            (0.93, 1.0),
        )

    def test_buckets_binarios_van_de_05_a_1_en_pasos_de_01(self) -> None:
        from ml.evaluation.calibration import BUCKETS_BINARIO

        assert BUCKETS_BINARIO == ((0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0))

    def test_buckets_para_mercado_resuelve_los_tres_mercados(self) -> None:
        from app.models.calibracion_historica import Mercado
        from ml.evaluation.calibration import BUCKETS_1X2, BUCKETS_BINARIO, buckets_para_mercado

        assert buckets_para_mercado(Mercado.UNO_X_DOS) == BUCKETS_1X2
        assert buckets_para_mercado(Mercado.OVER_UNDER_2_5) == BUCKETS_BINARIO
        assert buckets_para_mercado(Mercado.BTTS) == BUCKETS_BINARIO


class TestConstruirTablaCalibracion:
    def test_precision_empirica_es_la_fraccion_de_aciertos_del_bucket(self) -> None:
        from app.models.calibracion_historica import Mercado
        from ml.evaluation.calibration import construir_tabla_calibracion

        tabla = construir_tabla_calibracion(
            Mercado.BTTS,
            probabilidad_predicha=[0.65, 0.68, 0.61, 0.69],
            acierto=[True, True, True, False],
        )

        assert len(tabla) == 1
        bucket = tabla[0]
        assert bucket.rango_probabilidad_min == pytest.approx(0.6)
        assert bucket.rango_probabilidad_max == pytest.approx(0.7)
        assert bucket.precision_empirica == pytest.approx(3 / 4)
        assert bucket.n_observaciones == 4

    def test_solo_devuelve_buckets_con_al_menos_una_observacion(self) -> None:
        from app.models.calibracion_historica import Mercado
        from ml.evaluation.calibration import construir_tabla_calibracion

        tabla = construir_tabla_calibracion(
            Mercado.BTTS, probabilidad_predicha=[0.65], acierto=[True]
        )

        assert len(tabla) == 1

    def test_el_limite_inferior_del_bucket_es_inclusivo(self) -> None:
        """0.6 exacto cae en `[0.6, 0.7)`, no en `[0.5, 0.6)`."""
        from app.models.calibracion_historica import Mercado
        from ml.evaluation.calibration import construir_tabla_calibracion

        tabla = construir_tabla_calibracion(
            Mercado.BTTS, probabilidad_predicha=[0.6], acierto=[True]
        )

        assert tabla[0].rango_probabilidad_min == pytest.approx(0.6)

    def test_probabilidad_exactamente_1_cae_en_el_ultimo_bucket_cerrado(self) -> None:
        from app.models.calibracion_historica import Mercado
        from ml.evaluation.calibration import construir_tabla_calibracion

        tabla = construir_tabla_calibracion(
            Mercado.UNO_X_DOS, probabilidad_predicha=[1.0], acierto=[True]
        )

        assert tabla[0].rango_probabilidad_min == pytest.approx(0.93)
        assert tabla[0].rango_probabilidad_max == pytest.approx(1.0)


class TestNivelConfianzaDePrecision:
    def test_alta_desde_060_inclusive(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import nivel_confianza_de_precision

        assert nivel_confianza_de_precision(0.60, n_observaciones=30) == NivelConfianza.ALTA
        assert nivel_confianza_de_precision(0.75, n_observaciones=30) == NivelConfianza.ALTA

    def test_media_entre_045_y_060(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import nivel_confianza_de_precision

        assert nivel_confianza_de_precision(0.45, n_observaciones=30) == NivelConfianza.MEDIA
        assert nivel_confianza_de_precision(0.59, n_observaciones=30) == NivelConfianza.MEDIA

    def test_baja_debajo_de_045(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import nivel_confianza_de_precision

        assert nivel_confianza_de_precision(0.44, n_observaciones=30) == NivelConfianza.BAJA

    def test_baja_por_defecto_con_menos_de_30_observaciones_sin_mirar_precision(self) -> None:
        """ADR 0001: ni una precisión perfecta salva a un bucket con pocas
        observaciones — la regla de RF-005b, no una excepción."""
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import nivel_confianza_de_precision

        assert nivel_confianza_de_precision(1.0, n_observaciones=29) == NivelConfianza.BAJA

    def test_el_umbral_de_observaciones_es_configurable(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import nivel_confianza_de_precision

        assert (
            nivel_confianza_de_precision(0.70, n_observaciones=10, umbral_n_observaciones=5)
            == NivelConfianza.ALTA
        )


class TestBuscarNivelConfianza:
    def test_encuentra_el_bucket_que_contiene_la_probabilidad(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import BucketCalibracion, buscar_nivel_confianza

        tabla = [
            BucketCalibracion(0.5, 0.6, precision_empirica=0.40, n_observaciones=50),
            BucketCalibracion(0.6, 0.7, precision_empirica=0.65, n_observaciones=50),
        ]

        assert buscar_nivel_confianza(tabla, 0.63) == NivelConfianza.ALTA
        assert buscar_nivel_confianza(tabla, 0.55) == NivelConfianza.BAJA

    def test_probabilidad_sin_bucket_en_la_tabla_cae_a_baja(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import BucketCalibracion, buscar_nivel_confianza

        tabla = [BucketCalibracion(0.6, 0.7, precision_empirica=0.90, n_observaciones=50)]

        assert buscar_nivel_confianza(tabla, 0.55) == NivelConfianza.BAJA

    def test_tabla_vacia_cae_a_baja(self) -> None:
        from app.models.prediccion import NivelConfianza
        from ml.evaluation.calibration import buscar_nivel_confianza

        assert buscar_nivel_confianza([], 0.80) == NivelConfianza.BAJA
