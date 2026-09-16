"""
Modelo SQLAlchemy para Equipo (T007 de specs/001-prediccion-partido/tasks.md).
"""

import uuid

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.partido import Liga


class Equipo(Base):
    __tablename__ = "equipos"
    __table_args__ = (
        # data-model.md: evita duplicar equipos al cargar varias fuentes
        # históricas (sección 6.3) — protegido también por ml/data/alias.py.
        UniqueConstraint("nombre", "liga", name="uq_equipos_nombre_liga"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    liga: Mapped[Liga] = mapped_column(Enum(Liga, name="liga_enum"), nullable=False)
    # Derivado (data-model.md): dispara el aviso de baja confiabilidad de la
    # Historia 1 (RF-010). Lo calcula quien carga el histórico (T012b/T012c),
    # no una columna generada por la base de datos.
    tiene_historial_suficiente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
