"""
Modelo SQLAlchemy para CuotaMercado (T006 de
specs/003-track-record-publico/tasks.md).

Guarda probabilidades implícitas derivadas de la cuota, **nunca la cuota
cruda** — así este modelo de datos no puede alimentar un comparador de
casas de apuestas (Artículo V, RF-005). Fórmula de normalización con
descuento del margen de la casa en `data-model.md`.
"""

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FuenteCuota(enum.Enum):
    FOOTBALL_DATA = "football_data"
    KAGGLE = "kaggle"
    OPERATIVA = "operativa"


class CuotaMercado(Base):
    __tablename__ = "cuotas_mercado"
    __table_args__ = (
        # data-model.md: impide dos cuotas de la misma fuente para el
        # mismo partido — un partido puede tener una fila por fuente.
        UniqueConstraint("partido_id", "fuente", name="uq_cuotas_mercado_partido_fuente"),
        Index("ix_cuotas_mercado_partido_id", "partido_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partidos.id"), nullable=False
    )

    prob_implicita_local: Mapped[float] = mapped_column(Float, nullable=False)
    prob_implicita_empate: Mapped[float] = mapped_column(Float, nullable=False)
    prob_implicita_visitante: Mapped[float] = mapped_column(Float, nullable=False)

    fuente: Mapped[FuenteCuota] = mapped_column(
        Enum(
            FuenteCuota,
            name="fuente_cuota_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
