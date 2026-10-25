"""Modelo SQLAlchemy para Evidencia (noticia deportiva indexada).

Cumple con specs/002-explicacion-lenguaje-natural/data-model.md y RF-001/RF-002:
- `url` nico como clave de deduplicacin.
- `fecha_publicacion` NOT NULL con ndice para el filtro temporal del Artculo IV.
- `embedding` Vector(1024) (Titan Text Embeddings V2) con ndice HNSW.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.explicacion_evidencia import ExplicacionEvidencia


class Evidencia(Base):
    __tablename__ = "evidencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    texto_sanitizado: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    fuente: Mapped[str] = mapped_column(String(100), nullable=False, default="News API")

    # Titan Text Embeddings V2 usa 1024 dimensiones por defecto
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=False)

    equipo_relacionado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    partido_relacionado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Relacin N:M con Explicacion a travs de ExplicacionEvidencia
    explicaciones_asociadas: Mapped[list["ExplicacionEvidencia"]] = relationship(
        "ExplicacionEvidencia", back_populates="evidencia", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_evidencias_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
