"""
Esquemas Pydantic para la API de Explicaciones en Lenguaje Natural.
Basado en: specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceOut(BaseModel):
    """Esquema de cita de evidencia verificable (pilar 2 del product goal)."""
    id: UUID
    title: str = Field(..., description="Titular de la noticia/evidencia")
    url: str = Field(..., description="URL original verificable por el usuario")
    source: str = Field(..., description="Fuente de la noticia (ej. News API)")
    published_at: datetime = Field(..., description="Fecha de publicación UTC, siempre previa al kickoff")

    model_config = ConfigDict(from_attributes=True)


class ExplanationOut(BaseModel):
    """Respuesta para GET /api/matches/{match_id}/explanation"""
    match_id: UUID
    text: str = Field(..., description="Explicación en lenguaje natural (español)")
    is_fallback_no_evidence: bool = Field(
        False, description="True si no hubo evidencia suficiente y se usó el mensaje de ausencia de datos"
    )
    evidence: list[EvidenceOut] = Field(default_factory=list, description="Lista ordenada de fuentes citadas")
    generated_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FollowUpRequest(BaseModel):
    """Cuerpo del request para POST /api/matches/{match_id}/explanation/follow-up"""
    question: str = Field(..., min_length=3, max_length=500, description="Pregunta de seguimiento del usuario")


class FollowUpOut(BaseModel):
    """Respuesta para POST /api/matches/{match_id}/explanation/follow-up"""
    match_id: UUID
    question: str
    answer: str = Field(..., description="Respuesta a la pregunta basada en el contexto y SHAP")
    evidence: list[EvidenceOut] = Field(
        default_factory=list, description="Subconjunto de evidencia citada en la respuesta"
    )
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
