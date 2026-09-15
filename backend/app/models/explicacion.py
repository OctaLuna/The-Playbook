"""
Modelo SQLAlchemy para Explicación (1:1 con Predicción).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Explicacion(Base):
    __tablename__ = "explicaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    es_fallback_sin_evidencia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shap_features_usadas: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
