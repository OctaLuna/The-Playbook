"""
Modelo SQLAlchemy para Evidencia (noticias e información externa indexada).
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Evidencia(Base):
    __tablename__ = "evidencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(512), nullable=False)
    texto_sanitizado: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=True)
    fuente: Mapped[str] = mapped_column(String(128), nullable=False, default="News API")

    equipo_relacionado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    partido_relacionado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
