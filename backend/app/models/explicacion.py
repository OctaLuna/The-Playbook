"""Modelo SQLAlchemy para Explicación en Lenguaje Natural.

Cumple con specs/002-explicacion-lenguaje-natural/data-model.md y RF-001/RF-003:
- Relación 1:1 con Predicción (prediccion_id único).
- `es_fallback_sin_evidencia` para declarar ausencia honesta de datos (Historia 2).
- `shap_features_usadas` almacena congeladas las variables que más influyeron.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.explicacion_evidencia import ExplicacionEvidencia
    from app.models.pregunta_seguimiento import PreguntaSeguimiento


class Explicacion(Base):
    __tablename__ = "explicaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    prediccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    es_fallback_sin_evidencia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shap_features_usadas: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relación con tabla puente de evidencia citada (ordenada)
    evidencias_asociadas: Mapped[list["ExplicacionEvidencia"]] = relationship(
        "ExplicacionEvidencia",
        back_populates="explicacion",
        order_by="ExplicacionEvidencia.orden",
        cascade="all, delete-orphan",
    )

    # Relación 1:N con preguntas de seguimiento
    preguntas_seguimiento: Mapped[list["PreguntaSeguimiento"]] = relationship(
        "PreguntaSeguimiento",
        back_populates="explicacion",
        cascade="all, delete-orphan",
    )
