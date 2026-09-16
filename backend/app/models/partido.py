"""
Modelo SQLAlchemy para Partido (T006 de specs/001-prediccion-partido/tasks.md).

`Liga` se define acá porque T006 la introduce; `Equipo` (T007) la reutiliza —
una sola representación del enum de ligas, Artículo VIII.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Liga(enum.Enum):
    """Las 5 ligas del MVP (RF-008) — alcance fijo, sin future-proofing (Art. VII)."""

    PREMIER_LEAGUE = "premier_league"
    LALIGA = "laliga"
    SERIE_A = "serie_a"
    BUNDESLIGA = "bundesliga"
    LIGUE_1 = "ligue_1"


class EstadoPartido(enum.Enum):
    PROGRAMADO = "programado"
    JUGADO = "jugado"
    POSPUESTO = "pospuesto"
    CANCELADO = "cancelado"


class Partido(Base):
    __tablename__ = "partidos"
    __table_args__ = (
        # data-model.md "Índices y restricciones": la query del job de Celery
        # (RF-007) filtra por ventana de kickoff + estado programado.
        Index("ix_partidos_fecha_kickoff_estado", "fecha_kickoff", "estado"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liga: Mapped[Liga] = mapped_column(Enum(Liga, name="liga_enum"), nullable=False, index=True)
    equipo_local_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipos.id"), nullable=False
    )
    equipo_visitante_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipos.id"), nullable=False
    )
    fecha_kickoff: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[EstadoPartido] = mapped_column(
        Enum(EstadoPartido, name="estado_partido_enum"),
        nullable=False,
        default=EstadoPartido.PROGRAMADO,
    )
    # resultado_real (data-model.md): struct opcional, solo se llena cuando
    # estado = jugado. Dos columnas nullable en vez de un tipo compuesto —
    # Artículo VII, no hace falta más que esto para lo que pide el spec.
    goles_local: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goles_visitante: Mapped[int | None] = mapped_column(Integer, nullable=True)
