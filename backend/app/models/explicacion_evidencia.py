"""Tabla puente ExplicacionEvidencia (relación N:M).

Cumple con specs/002-explicacion-lenguaje-natural/data-model.md:
- PK compuesta (explicacion_id, evidencia_id).
- Columna `orden` para preservar la posición de las citas en el texto generado.
- Garantiza integridad referencial nativa sin usar arrays sin restricciones (Art. VIII).
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.evidencia import Evidencia
    from app.models.explicacion import Explicacion


class ExplicacionEvidencia(Base):
    __tablename__ = "explicacion_evidencias"

    explicacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("explicaciones.id", ondelete="CASCADE"),
        primary_key=True,
    )
    evidencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidencias.id", ondelete="CASCADE"),
        primary_key=True,
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    explicacion: Mapped["Explicacion"] = relationship(
        "Explicacion", back_populates="evidencias_asociadas"
    )
    evidencia: Mapped["Evidencia"] = relationship(
        "Evidencia", back_populates="explicaciones_asociadas"
    )
