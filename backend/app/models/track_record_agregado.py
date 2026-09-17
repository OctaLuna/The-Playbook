"""
Modelo SQLAlchemy para TrackRecordAgregado (T005 de
specs/003-track-record-publico/tasks.md).

Tabla cacheada, recalculada por el job diario de Celery (T011, RF-008). Una
fila por combinación (liga, mercado): el panel muestra el desempeño de cada
mercado por separado, nunca un agregado que los mezcle.
"""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Enum, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.calibracion_historica import Mercado
from app.models.partido import Liga


class TrackRecordAgregado(Base):
    __tablename__ = "track_record_agregado"
    __table_args__ = (
        # data-model.md: una sola fila vigente por combinación, el job la
        # reemplaza en vez de acumularla. Postgres no compara NULL como
        # igual a sí mismo, así que esto NO impide dos filas con
        # liga=NULL para el mismo (mercado, ventana_n) — T011 (el job)
        # debe borrar la fila global existente antes de insertar la nueva,
        # no puede apoyarse solo en esta restricción para ese caso.
        UniqueConstraint(
            "liga", "mercado", "ventana_n", name="uq_track_record_agregado_liga_mercado_ventana"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # NULL = agregado global; con valor = agregado filtrado por liga (RF-007).
    liga: Mapped[Liga | None] = mapped_column(Enum(Liga, name="liga_enum"), nullable=True)
    mercado: Mapped[Mercado] = mapped_column(
        Enum(
            Mercado,
            name="mercado_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    ventana_n: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    porcentaje_aciertos: Mapped[float] = mapped_column(Float, nullable=False)
    brier_promedio: Mapped[float] = mapped_column(Float, nullable=False)
    log_loss_promedio: Mapped[float] = mapped_column(Float, nullable=False)
    # data-model.md: solo en la fila mercado=1x2, y solo sobre partidos con
    # tiene_cuota_mercado=true.
    log_loss_mercado_promedio: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Tamaño real de la muestra — puede ser menor que ventana_n (RF-009).
    n_partidos_incluidos: Mapped[int] = mapped_column(Integer, nullable=False)
    # Versiones presentes en la ventana; más de un elemento => la serie no
    # es continua (reentrenamiento a mitad de ventana, T017b).
    versiones_modelo: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    calculado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
