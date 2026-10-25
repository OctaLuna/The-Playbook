"""Contratos estructurales de los modelos ya creados para 002."""

from app.models.evidencia import Evidencia
from app.models.explicacion import Explicacion
from app.models.explicacion_evidencia import ExplicacionEvidencia
from app.models.pregunta_seguimiento import PreguntaSeguimiento


def test_explicacion_es_unica_por_prediccion_y_tiene_fk() -> None:
    columna = Explicacion.__table__.c.prediccion_id

    assert columna.unique is True
    assert {fk.target_fullname for fk in columna.foreign_keys} == {"predicciones.id"}
    assert "es_fallback_sin_evidencia" in Explicacion.__table__.c
    assert "shap_features_usadas" in Explicacion.__table__.c


def test_evidencia_respeta_el_contrato_de_retrieval() -> None:
    tabla = Evidencia.__table__

    assert tabla.c.embedding.type.dim == 1024
    assert tabla.c.fecha_publicacion.nullable is False
    assert tabla.c.url.unique is True
    assert "titulo" in tabla.c


def test_modelos_de_citas_y_seguimiento_tienen_claves_requeridas() -> None:
    assert {col.name for col in ExplicacionEvidencia.__table__.primary_key.columns} == {
        "explicacion_id",
        "evidencia_id",
    }
    assert "orden" in ExplicacionEvidencia.__table__.c
    assert PreguntaSeguimiento.__table__.c.explicacion_id.nullable is False
    assert "pregunta" in PreguntaSeguimiento.__table__.c
    assert "respuesta" in PreguntaSeguimiento.__table__.c
