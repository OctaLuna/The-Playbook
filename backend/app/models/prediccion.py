"""
Modelo SQLAlchemy para Predicción (T008 de specs/001-prediccion-partido/tasks.md).

Relación 1:1 con Partido (data-model.md): si el partido se reprograma, se
conserva la predicción original, no se regenera.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NivelConfianza(enum.Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class Predicción(Base):
    __tablename__ = "predicciones"
    __table_args__ = (
        # data-model.md: la relación es 1:1 — sin esto, un job de Celery
        # reejecutado generaría una segunda predicción y GET /prediction
        # devolvería una arbitraria.
        UniqueConstraint("partido_id", name="uq_predicciones_partido_id"),
        CheckConstraint(
            "prob_local + prob_empate + prob_visitante BETWEEN 0.999999 AND 1.000001",
            name="ck_predicciones_1x2_suma_1",
        ),
        CheckConstraint(
            "prob_local BETWEEN 0 AND 1"
            " AND prob_empate BETWEEN 0 AND 1"
            " AND prob_visitante BETWEEN 0 AND 1"
            " AND prob_over_2_5 BETWEEN 0 AND 1"
            " AND prob_btts_si BETWEEN 0 AND 1",
            name="ck_predicciones_probabilidades_en_rango",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partidos.id"), nullable=False
    )

    # 1X2: se guardan las tres — ninguna se deriva trivialmente de las otras
    # dos sin arrastrar error de redondeo (data-model.md).
    prob_local: Mapped[float] = mapped_column(Float, nullable=False)
    prob_empate: Mapped[float] = mapped_column(Float, nullable=False)
    prob_visitante: Mapped[float] = mapped_column(Float, nullable=False)

    # Única línea O/U del MVP. prob_under_2_5 NO se persiste (Art. VIII: una
    # sola representación) — el schema la deriva como 1 - prob_over_2_5.
    prob_over_2_5: Mapped[float] = mapped_column(Float, nullable=False)
    # prob_btts_no tampoco se persiste, misma razón.
    prob_btts_si: Mapped[float] = mapped_column(Float, nullable=False)

    xg_local: Mapped[float] = mapped_column(Float, nullable=False)
    xg_visitante: Mapped[float] = mapped_column(Float, nullable=False)

    nivel_confianza: Mapped[NivelConfianza] = mapped_column(
        # Sin values_callable, SQLAlchemy persiste el .name del enum
        # ("ALTA") en vez del .value ("alta") que crea la migración —
        # mismo caso que CalibraciónHistórica.mercado en el otro modelo.
        Enum(
            NivelConfianza,
            name="nivel_confianza_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    head_to_head_disponible: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Campo interno (data-model.md): no se expone en la API pública por
    # defecto; lo consume 002 vía backend/app/services/.
    top_shap_features: Mapped[dict] = mapped_column(JSON, nullable=False)

    version_modelo: Mapped[str] = mapped_column(String(128), nullable=False)
    generado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
