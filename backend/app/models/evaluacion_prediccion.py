"""
Modelo SQLAlchemy para EvaluaciónPredicción (T004 de
specs/003-track-record-publico/tasks.md).

Relación 1:1 con `Predicción` (001); solo existe para partidos con
`estado = jugado` — quien la crea (T009/T011) es responsable de esa regla,
no una restricción de esta tabla. Evalúa los **tres** mercados
probabilísticos que el modelo predice, no solo 1X2 (data-model.md).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EvaluaciónPredicción(Base):
    __tablename__ = "evaluaciones_prediccion"
    __table_args__ = (
        # data-model.md: la relación es 1:1 — sin esto, un job diario
        # reejecutado duplicaría la evaluación y sesgaría el agregado.
        UniqueConstraint("prediccion_id", name="uq_evaluaciones_prediccion_prediccion_id"),
        # data-model.md: consulta de la ventana distinguiendo versiones
        # (reentrenamiento a mitad de ventana, T017b).
        Index("ix_evaluaciones_version_modelo_evaluado_en", "version_modelo", "evaluado_en"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partidos.id"), nullable=False
    )
    prediccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predicciones.id"), nullable=False
    )

    acierto_1x2: Mapped[bool] = mapped_column(Boolean, nullable=False)
    acierto_over_under_2_5: Mapped[bool] = mapped_column(Boolean, nullable=False)
    acierto_btts: Mapped[bool] = mapped_column(Boolean, nullable=False)

    brier_1x2: Mapped[float] = mapped_column(Float, nullable=False)
    brier_over_under_2_5: Mapped[float] = mapped_column(Float, nullable=False)
    brier_btts: Mapped[float] = mapped_column(Float, nullable=False)

    log_loss_1x2: Mapped[float] = mapped_column(Float, nullable=False)
    log_loss_over_under_2_5: Mapped[float] = mapped_column(Float, nullable=False)
    log_loss_btts: Mapped[float] = mapped_column(Float, nullable=False)

    # data-model.md: false si no había CuotaMercado para este partido (caso
    # límite de T018) — el baseline de mercado solo se calcula en 1X2.
    tiene_cuota_mercado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    log_loss_mercado_1x2: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Copiado de Predicción.version_modelo al evaluar — congelarlo acá es lo
    # que permite distinguir versiones cuando hay un reentrenamiento a
    # mitad de ventana (T017b), no una FK a un valor que puede cambiar.
    version_modelo: Mapped[str] = mapped_column(String(128), nullable=False)
    evaluado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
