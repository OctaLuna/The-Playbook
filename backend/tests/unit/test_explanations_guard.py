"""Guarda de contradicción de explicaciones (`app.services.explanations_service`).

Cuando la guarda descarta el texto del modelo y lo reemplaza por la plantilla, debe dejar
rastro del motivo y del texto original: sin eso no se puede medir con qué frecuencia ocurre,
y la revisión manual de groundedness (T022) acabaría evaluando solo la plantilla.

Las pruebas marcadas "documenta el comportamiento actual" fijan lo que la guarda hace HOY,
incluidos sus límites; si el equipo decide afinarla, deben cambiar a propósito.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

import pytest

from app.models.prediccion import Predicción
from app.services.explanations_service import (
    _prediction_contradiction_reason,
    _registrar_reemplazo_de_guarda,
)

pytestmark = pytest.mark.unit


def _prediccion() -> Predicción:
    return Predicción(
        prob_local=0.65,
        prob_empate=0.22,
        prob_visitante=0.13,
        prob_over_2_5=0.55,
        prob_btts_si=0.48,
        xg_local=1.8,
        xg_visitante=0.9,
        top_shap_features={"forma_local": 0.3},
        version_modelo="test",
        generado_en=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_texto_con_probabilidades_de_la_prediccion_pasa_la_guarda() -> None:
    texto = "El modelo da 65% al local, 22% al empate y 13% a la visita."
    assert _prediction_contradiction_reason(texto, _prediccion()) is None


def test_porcentaje_redondeado_dentro_de_medio_punto_pasa() -> None:
    assert _prediction_contradiction_reason("Probabilidad de 65,4%.", _prediccion()) is None


def test_una_frase_de_resultado_se_descarta_con_su_motivo() -> None:
    motivo = _prediction_contradiction_reason(
        "Se espera que el local ganará con comodidad.", _prediccion()
    )
    assert motivo is not None
    assert "frase de resultado" in motivo
    assert "'el local ganará'" in motivo  # la frase exacta que apareció en el texto


def test_un_porcentaje_ajeno_a_la_prediccion_se_descarta_con_su_motivo() -> None:
    motivo = _prediction_contradiction_reason(
        "El equipo promedia 60% de posesión según la crónica.", _prediccion()
    )
    assert motivo is not None
    assert "porcentaje 60%" in motivo


def test_documenta_el_comportamiento_actual_la_frase_negada_tambien_se_descarta() -> None:
    """La guarda no entiende la negación: descarta aunque el texto NO afirme el resultado."""
    motivo = _prediction_contradiction_reason(
        "El modelo no afirma que haya victoria local.", _prediccion()
    )
    assert motivo is not None


def test_documenta_el_comportamiento_actual_un_porcentaje_de_la_evidencia_se_descarta() -> None:
    """Un dato legítimo de una noticia (no del modelo) basta para reemplazar el texto."""
    motivo = _prediction_contradiction_reason(
        "Según la crónica, ganó el 80% de sus duelos.", _prediccion()
    )
    assert motivo is not None


def test_el_reemplazo_registra_motivo_partido_y_texto_original(
    caplog: pytest.LogCaptureFixture,
) -> None:
    partido = uuid.uuid4()
    with caplog.at_level(logging.WARNING, logger="app.services.explanations_service"):
        _registrar_reemplazo_de_guarda(
            "explicación", partido, "frase de resultado: 'victoria local'", "Texto del modelo"
        )

    registro = caplog.records[0]
    mensaje = registro.getMessage()
    assert registro.levelno == logging.WARNING
    assert str(partido) in mensaje
    assert "frase de resultado: 'victoria local'" in mensaje
    assert "Texto del modelo" in mensaje


def test_el_registro_recorta_textos_muy_largos(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="app.services.explanations_service"):
        _registrar_reemplazo_de_guarda("seguimiento", uuid.uuid4(), "m", "x" * 5000)

    assert "x" * 2000 in caplog.records[0].getMessage()
    assert "x" * 2001 not in caplog.records[0].getMessage()
