"""Tabla de calibración empírica y badge de confianza (ml-design.md §6).

El nivel de confianza SIEMPRE sale de la precisión histórica observada por
bucket de probabilidad predicha — nunca de la distancia a un reparto
uniforme (ADR 0001, `docs/adr/0001-badge-confianza-calibrado.md`). Este
módulo construye la tabla desde el backtesting cronológico y resuelve el
lookup (mercado, probabilidad) → `NivelConfianza`.

Reutiliza `NivelConfianza` (`app.models.prediccion`) y `Mercado`
(`app.models.calibracion_historica`) tal cual — Artículo VIII, una sola
representación del enum en todo el repo.

Ver `backend/tests/unit/test_calibration.py` para el contrato completo.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.calibracion_historica import Mercado
from app.models.prediccion import NivelConfianza

ANCHO_BUCKET = 0.1
MINIMO_1X2 = 0.33
MINIMO_BINARIO = 0.5
MAXIMO = 1.0

# ml-design.md §6: >=0.60 Alta, [0.45,0.60) Media, <0.45 Baja.
UMBRAL_ALTA = 0.60
UMBRAL_MEDIA = 0.45
# Regla clásica del límite central, fijada como default de Sprint 0 — se
# revisa con datos reales de backtesting (ml-design.md §6).
UMBRAL_N_OBSERVACIONES_DEFAULT = 30


def _generar_buckets(
    minimo: float, maximo: float, ancho: float = ANCHO_BUCKET
) -> tuple[tuple[float, float], ...]:
    """Buckets de ancho `ancho` entre `minimo` y `maximo`; el último se
    recorta a `maximo` en vez de sobrepasarlo (`1.0 - 0.33` no es múltiplo
    exacto de `0.1`)."""
    buckets: list[tuple[float, float]] = []
    inicio = round(minimo, 10)
    while inicio < maximo:
        fin = round(min(inicio + ancho, maximo), 10)
        buckets.append((inicio, fin))
        inicio = fin
    return tuple(buckets)


BUCKETS_1X2 = _generar_buckets(MINIMO_1X2, MAXIMO)
BUCKETS_BINARIO = _generar_buckets(MINIMO_BINARIO, MAXIMO)

_BUCKETS_POR_MERCADO: dict[Mercado, tuple[tuple[float, float], ...]] = {
    Mercado.UNO_X_DOS: BUCKETS_1X2,
    Mercado.OVER_UNDER_2_5: BUCKETS_BINARIO,
    Mercado.BTTS: BUCKETS_BINARIO,
}


@dataclass(frozen=True)
class BucketCalibracion:
    rango_probabilidad_min: float
    rango_probabilidad_max: float
    precision_empirica: float
    n_observaciones: int


def buckets_para_mercado(mercado: Mercado) -> tuple[tuple[float, float], ...]:
    """`[0.33, 1.0]` para 1X2 (el mínimo posible es 1/3), `[0.5, 1.0]` para
    los mercados binarios (el mínimo posible es 0.5) — ml-design.md §6."""
    return _BUCKETS_POR_MERCADO[mercado]


def _bucket_de(
    probabilidad: float, buckets: tuple[tuple[float, float], ...]
) -> tuple[float, float]:
    """Límite inferior inclusivo, superior exclusivo — salvo el último
    bucket, cerrado en `MAXIMO` para que `probabilidad == 1.0` caiga en
    algún lado."""
    for i, (minimo, maximo) in enumerate(buckets):
        es_ultimo = i == len(buckets) - 1
        if minimo <= probabilidad < maximo or (es_ultimo and probabilidad == maximo):
            return (minimo, maximo)
    raise ValueError(f"{probabilidad} no cae en ningún bucket de {buckets}.")


def construir_tabla_calibracion(
    mercado: Mercado,
    probabilidad_predicha: list[float],
    acierto: list[bool],
) -> list[BucketCalibracion]:
    """Agrupa `(probabilidad_predicha, acierto)` en los buckets de
    `mercado` y calcula `precision_empirica` por bucket. `probabilidad_predicha`
    es la probabilidad del resultado más probable de cada predicción de
    validación (ml-design.md §6, paso 1) — no de un resultado fijo. Solo
    devuelve buckets con al menos una observación."""
    buckets = buckets_para_mercado(mercado)
    aciertos_por_bucket: dict[tuple[float, float], list[bool]] = {b: [] for b in buckets}

    for probabilidad, acerto in zip(probabilidad_predicha, acierto, strict=True):
        bucket = _bucket_de(probabilidad, buckets)
        aciertos_por_bucket[bucket].append(acerto)

    return [
        BucketCalibracion(
            rango_probabilidad_min=minimo,
            rango_probabilidad_max=maximo,
            precision_empirica=sum(observaciones) / len(observaciones),
            n_observaciones=len(observaciones),
        )
        for (minimo, maximo), observaciones in aciertos_por_bucket.items()
        if observaciones
    ]


def nivel_confianza_de_precision(
    precision_empirica: float,
    n_observaciones: int,
    umbral_n_observaciones: int = UMBRAL_N_OBSERVACIONES_DEFAULT,
) -> NivelConfianza:
    """Mapeo de `precision_empirica` a badge (ml-design.md §6): menos de
    `umbral_n_observaciones` cae a Baja sin mirar `precision_empirica`
    siquiera — RF-005b, ADR 0001."""
    if n_observaciones < umbral_n_observaciones:
        return NivelConfianza.BAJA
    if precision_empirica >= UMBRAL_ALTA:
        return NivelConfianza.ALTA
    if precision_empirica >= UMBRAL_MEDIA:
        return NivelConfianza.MEDIA
    return NivelConfianza.BAJA


def buscar_nivel_confianza(
    tabla: list[BucketCalibracion],
    probabilidad_predicha: float,
    umbral_n_observaciones: int = UMBRAL_N_OBSERVACIONES_DEFAULT,
) -> NivelConfianza:
    """Lookup (rango de probabilidad) → `NivelConfianza` sobre `tabla`, que
    ya debe venir filtrada por mercado (por ejemplo, por la query de
    `CalibraciónHistórica` del servicio que llama a esto). Ningún bucket
    cubre `probabilidad_predicha` (nunca hubo observaciones ahí) → Baja,
    mismo criterio conservador que "menos del umbral"."""
    for bucket in tabla:
        cubre_probabilidad = (
            bucket.rango_probabilidad_min <= probabilidad_predicha < bucket.rango_probabilidad_max
        )
        es_borde_superior_cerrado = probabilidad_predicha == bucket.rango_probabilidad_max == MAXIMO
        if cubre_probabilidad or es_borde_superior_cerrado:
            return nivel_confianza_de_precision(
                bucket.precision_empirica, bucket.n_observaciones, umbral_n_observaciones
            )
    return NivelConfianza.BAJA
