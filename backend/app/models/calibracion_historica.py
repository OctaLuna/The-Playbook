"""
Modelo SQLAlchemy para CalibraciónHistórica (T009 de
specs/001-prediccion-partido/tasks.md).

Tabla de lookup independiente (data-model.md): no está asociada a un partido
específico, la recalcula el job de backtesting (ml-design.md §6).
"""

import enum
import uuid

from sqlalchemy import Enum, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Mercado(enum.Enum):
    UNO_X_DOS = "1x2"
    OVER_UNDER_2_5 = "over_under_2_5"
    BTTS = "btts"


class CalibraciónHistórica(Base):
    __tablename__ = "calibraciones_historicas"
    __table_args__ = (
        # data-model.md: un solo bucket vigente por mercado y versión; el
        # backtesting lo reemplaza, no lo acumula.
        UniqueConstraint(
            "mercado",
            "rango_probabilidad_min",
            "version_modelo",
            name="uq_calibracion_mercado_rango_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mercado: Mapped[Mercado] = mapped_column(
        # sqlalchemy.Enum usaría el .name de Mercado ("UNO_X_DOS") como
        # valor de columna por defecto; values_callable fuerza a persistir
        # el .value real ("1x2"), que es el que compara ml/evaluation/
        # (Artículo VIII: una sola representación del string de mercado).
        Enum(
            Mercado,
            name="mercado_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    rango_probabilidad_min: Mapped[float] = mapped_column(Float, nullable=False)
    rango_probabilidad_max: Mapped[float] = mapped_column(Float, nullable=False)
    precision_empirica: Mapped[float] = mapped_column(Float, nullable=False)
    # Si es menor al umbral mínimo (default 30, ml-design.md §6), el badge
    # cae a "baja" por defecto — la lógica del umbral vive en T013, acá solo
    # el campo.
    n_observaciones: Mapped[int] = mapped_column(Integer, nullable=False)
    version_modelo: Mapped[str] = mapped_column(String(128), nullable=False)
