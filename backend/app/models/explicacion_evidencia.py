"""
Tabla puente SQLAlchemy entre Explicación y Evidencia (relación N:M con orden de cita).
"""

import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExplicacionEvidencia(Base):
    __tablename__ = "explicacion_evidencia"

    explicacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("explicaciones.id", ondelete="CASCADE"), primary_key=True
    )
    evidencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidencias.id", ondelete="CASCADE"), primary_key=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
