"""Guardián del Artículo V — Independencia del Mercado.

La constitución (`memory/constitution.md`, Artículo V) exige:

    "Ninguna columna derivada de cuotas puede formar parte del feature set de
     entrenamiento de Dixon-Coles, XGBoost o LSTM. Un test automatizado en
     `backend/ml/features/` debe fallar el build si alguna columna de odds llega
     al feature set de entrenamiento."

Este archivo es ese test. Es el guardián del diferencial declarado del proyecto: una
predicción **independiente** del consenso de mercado. Si una columna de cuotas se cuela
en el entrenamiento, el modelo aprende a imitar a las casas de apuestas y la comparación
del track record (feature 003) contra el baseline de mercado deja de significar nada
— estaría comparando el mercado consigo mismo.

Las cuotas sí se usan, pero solo para calcular el baseline interno de log-loss. Ese uso
vive en `ml/evaluation/`, nunca en `ml/features/`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ_ML = Path(__file__).resolve().parents[1]

# Nomenclatura de Football-Data.co.uk y del dataset de Kaggle (docs/project_spec.md §6.2):
# B365H/D/A, BWH, IWH, PSH, WHH, VCH, MaxH, AvgH... más los nombres genéricos.
PATRONES_DE_CUOTAS = [
    re.compile(r"\bB365[HDA]\b"),
    re.compile(r"\b(?:BW|IW|PS|WH|VC|GB|SJ|LB|SB)[HDA]\b"),
    re.compile(r"\b(?:Max|Avg)C?[HDA]\b"),
    re.compile(r"(?i)\bodds?\b"),
    re.compile(r"(?i)\bcuotas?\b"),
    re.compile(r"(?i)\bbookmaker"),
    re.compile(r"(?i)\bimplied_prob"),
]

# `ml/evaluation/` sí puede tocar cuotas: ahí vive el baseline de mercado.
DIRECTORIOS_VIGILADOS = ("features", "models", "ensemble")


def _archivos_de_features() -> list[Path]:
    archivos: list[Path] = []
    for sub in DIRECTORIOS_VIGILADOS:
        archivos += [
            p
            for p in (RAIZ_ML / sub).rglob("*.py")
            if not p.name.startswith("test_") and "__pycache__" not in p.parts
        ]
    return archivos


@pytest.mark.constitucional
def test_ninguna_columna_de_cuotas_aparece_en_el_pipeline_de_features() -> None:
    """Artículo V: las cuotas no entran al feature set de entrenamiento."""
    infracciones: list[str] = []

    for archivo in _archivos_de_features():
        for n, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
            codigo = linea.split("#", 1)[0]  # los comentarios pueden nombrarlas
            for patron in PATRONES_DE_CUOTAS:
                if patron.search(codigo):
                    infracciones.append(
                        f"{archivo.relative_to(RAIZ_ML.parent)}:{n} — {linea.strip()}"
                    )
                    break

    assert not infracciones, (
        "Artículo V (Independencia del Mercado) violado — referencia a cuotas en el "
        "pipeline de entrenamiento:\n  "
        + "\n  ".join(infracciones)
        + "\n\nLas cuotas solo pueden usarse para el baseline de log-loss, en "
        "backend/ml/evaluation/. Ver docs/project_spec.md §9 y el Artículo V."
    )


@pytest.mark.constitucional
@pytest.mark.pendiente_implementacion
def test_el_feature_set_construido_no_contiene_columnas_de_cuotas() -> None:
    """Contrato de `ml.features.build.construir_feature_set`.

    **ROJO a propósito.** La función aún no existe: fase Red del Artículo III, y debe
    fallar hasta que la tarea T012 de 001 la implemente.

    El guardián estático de arriba mira el código; este mira el resultado real, que es
    lo que de verdad importa cuando las columnas se seleccionan de forma dinámica.
    """
    from ml.features.build import construir_feature_set  # type: ignore[import-not-found]

    columnas = construir_feature_set(partidos=[])

    contaminadas = [
        c for c in columnas if any(p.search(str(c)) for p in PATRONES_DE_CUOTAS)
    ]
    assert not contaminadas, (
        f"El feature set incluye columnas derivadas de cuotas: {contaminadas}. "
        "El modelo aprendería a imitar al mercado en vez de predecir de forma independiente."
    )
