"""Guardián del Artículo IV — Integridad Temporal.

La constitución (`memory/constitution.md`, Artículo IV) exige:

    "Split cronológico obligatorio, nunca aleatorio... Un test automatizado en
     `backend/ml/evaluation/` debe fallar el build si algún pipeline usa
     `train_test_split` sin el parámetro de orden temporal."

Este archivo es ese test. Combina dos capas:

1. Un **guardián estático** que recorre el código de `ml/` buscando splits aleatorios.
   Pasa hoy (no hay código) y sigue vigilando cuando lo haya.
2. Un **contrato de comportamiento** sobre `ml.evaluation.split`, que todavía no existe.
   Falla ahora a propósito: es la fase Red del Artículo III.

Por qué importa: entrenar con un split aleatorio deja que el modelo "vea" partidos
posteriores al que predice. El modelo parece bueno en validación y es inútil en
producción — y el track record público (feature 003) sería deshonesto. Es el error
clásico en datos deportivos y el diferencial ético declarado del proyecto.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RAIZ_ML = Path(__file__).resolve().parents[1]

# `train_test_split` de scikit-learn baraja por defecto (shuffle=True). Solo es
# aceptable si se desactiva explícitamente.
PARAMETROS_QUE_DESACTIVAN_EL_BARAJADO = {"shuffle"}


def _archivos_python_de_ml() -> list[Path]:
    return [
        p
        for p in RAIZ_ML.rglob("*.py")
        if not p.name.startswith("test_") and "__pycache__" not in p.parts
    ]


def _llamadas(arbol: ast.AST, nombre: str) -> list[ast.Call]:
    encontradas = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue
        func = nodo.func
        llamado = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if llamado == nombre:
            encontradas.append(nodo)
    return encontradas


@pytest.mark.constitucional
def test_ningun_pipeline_usa_train_test_split_aleatorio() -> None:
    """Artículo IV: ningún split puede barajar los partidos."""
    infracciones: list[str] = []

    for archivo in _archivos_python_de_ml():
        arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))

        for llamada in _llamadas(arbol, "train_test_split"):
            kwargs = {k.arg for k in llamada.keywords if k.arg}
            if not (kwargs & PARAMETROS_QUE_DESACTIVAN_EL_BARAJADO):
                infracciones.append(
                    f"{archivo.relative_to(RAIZ_ML.parent)}:{llamada.lineno} — "
                    f"train_test_split sin shuffle=False"
                )

    assert not infracciones, (
        "Artículo IV (Integridad Temporal) violado — split aleatorio detectado:\n  "
        + "\n  ".join(infracciones)
        + "\n\nUsa un corte por fecha: entrena con partidos anteriores a la fecha de corte "
        "y valida con posteriores. Ver docs/project_spec.md §6.5."
    )


@pytest.mark.constitucional
@pytest.mark.pendiente_implementacion
def test_el_split_cronologico_no_deja_pasar_partidos_futuros_al_entrenamiento() -> None:
    """Contrato de `ml.evaluation.split.split_cronologico`.

    **ROJO a propósito.** La función aún no existe: esta es la fase Red del Artículo III,
    y debe fallar hasta que la tarea T012 de 001 la implemente. No está marcado como
    `skip` deliberadamente — un test que se salta no vigila nada, y el Artículo III exige
    *confirmar que falla* antes de escribir el código.

    Al implementarla debe cumplir que *toda* fecha de entrenamiento sea estrictamente
    anterior a *toda* fecha de validación.
    """
    from datetime import date

    from ml.evaluation.split import split_cronologico  # type: ignore[import-not-found]

    partidos = [{"fecha": date(2024, 1, i + 1), "id": i} for i in range(100)]
    entrenamiento, validacion = split_cronologico(partidos, fecha_corte=date(2024, 2, 20))

    assert entrenamiento and validacion, "Ambos conjuntos deben tener partidos"
    assert max(p["fecha"] for p in entrenamiento) < min(p["fecha"] for p in validacion), (
        "Fuga temporal: hay partidos de entrenamiento posteriores a partidos de validación"
    )
