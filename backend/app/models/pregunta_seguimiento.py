"""Modelo SQLAlchemy para PreguntaSeguimiento (Historia 4 / RF-005).

Cumple con specs/002-explicacion-lenguaje-natural/data-model.md:
- Relación N:1 con Explicacion.
- Permite profundizar en el contexto inicial sin introducir nuevas predicciones.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.explicacion import Explicacion


class PreguntaSeguimiento(Base):
    __tablename__ = "preguntas_seguimiento"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    explicacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("explicaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pregunta: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta: Mapped[str] = mapped_column(Text, nullable=False)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    explicacion: Mapped["Explicacion"] = relationship(
        "Explicacion", back_populates="preguntas_seguimiento"
    )
