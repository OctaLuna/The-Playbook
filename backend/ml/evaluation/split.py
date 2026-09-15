"""Split cronológico para entrenamiento/validación (Artículo IV).

Ver `test_split_cronologico.py` para el contrato completo.
"""

from __future__ import annotations

from datetime import date
from typing import Any


def split_cronologico(
    partidos: list[dict[str, Any]], fecha_corte: date
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Divide `partidos` en entrenamiento (antes de `fecha_corte`) y validación
    (`fecha_corte` en adelante), nunca aleatorio.

    Cada partido es un dict con una clave `"fecha"` (`date`). `fecha_corte` es
    inclusiva del lado de validación: un partido en esa fecha exacta nunca se
    filtra a entrenamiento.
    """
    entrenamiento = [p for p in partidos if p["fecha"] < fecha_corte]
    validacion = [p for p in partidos if p["fecha"] >= fecha_corte]
    return entrenamiento, validacion
