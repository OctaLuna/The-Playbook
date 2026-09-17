"""crear tablas evaluaciones_prediccion, track_record_agregado y cuotas_mercado (T004-T007)

Revision ID: 2e87cd87231a
Revises: 7a8291b09210
Create Date: 2026-09-17 11:52:40.812343

Reutiliza los enums `liga_enum` (definido en 52cb67a25dcc, valores en
MAYÚSCULA — el `.name`, sin `values_callable`) y `mercado_enum` (definido en
1bfdd75d48c4, valores en minúscula vía `values_callable`) tal cual existen
en la base — Artículo VIII, una sola representación de cada enum. Solo
`fuente_cuota_enum` es nuevo en esta revisión.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e87cd87231a"
down_revision: str | Sequence[str] | None = "7a8291b09210"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LIGA_ENUM = postgresql.ENUM(
    "PREMIER_LEAGUE",
    "LALIGA",
    "SERIE_A",
    "BUNDESLIGA",
    "LIGUE_1",
    name="liga_enum",
    create_type=False,
)
MERCADO_ENUM = postgresql.ENUM(
    "1x2", "over_under_2_5", "btts", name="mercado_enum", create_type=False
)
FUENTE_CUOTA_ENUM = postgresql.ENUM(
    "football_data", "kaggle", "operativa", name="fuente_cuota_enum", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    FUENTE_CUOTA_ENUM.create(bind, checkfirst=True)

    op.create_table(
        "evaluaciones_prediccion",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "partido_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partidos.id"),
            nullable=False,
        ),
        sa.Column(
            "prediccion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("predicciones.id"),
            nullable=False,
        ),
        sa.Column("acierto_1x2", sa.Boolean(), nullable=False),
        sa.Column("acierto_over_under_2_5", sa.Boolean(), nullable=False),
        sa.Column("acierto_btts", sa.Boolean(), nullable=False),
        sa.Column("brier_1x2", sa.Float(), nullable=False),
        sa.Column("brier_over_under_2_5", sa.Float(), nullable=False),
        sa.Column("brier_btts", sa.Float(), nullable=False),
        sa.Column("log_loss_1x2", sa.Float(), nullable=False),
        sa.Column("log_loss_over_under_2_5", sa.Float(), nullable=False),
        sa.Column("log_loss_btts", sa.Float(), nullable=False),
        sa.Column("tiene_cuota_mercado", sa.Boolean(), nullable=False),
        sa.Column("log_loss_mercado_1x2", sa.Float(), nullable=True),
        sa.Column("version_modelo", sa.String(128), nullable=False),
        sa.Column("evaluado_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("prediccion_id", name="uq_evaluaciones_prediccion_prediccion_id"),
    )
    op.create_index(
        "ix_evaluaciones_version_modelo_evaluado_en",
        "evaluaciones_prediccion",
        ["version_modelo", "evaluado_en"],
    )

    op.create_table(
        "track_record_agregado",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("liga", LIGA_ENUM, nullable=True),
        sa.Column("mercado", MERCADO_ENUM, nullable=False),
        sa.Column("ventana_n", sa.Integer(), nullable=False),
        sa.Column("porcentaje_aciertos", sa.Float(), nullable=False),
        sa.Column("brier_promedio", sa.Float(), nullable=False),
        sa.Column("log_loss_promedio", sa.Float(), nullable=False),
        sa.Column("log_loss_mercado_promedio", sa.Float(), nullable=True),
        sa.Column("n_partidos_incluidos", sa.Integer(), nullable=False),
        sa.Column("versiones_modelo", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("calculado_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "liga", "mercado", "ventana_n", name="uq_track_record_agregado_liga_mercado_ventana"
        ),
    )

    op.create_table(
        "cuotas_mercado",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "partido_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partidos.id"),
            nullable=False,
        ),
        sa.Column("prob_implicita_local", sa.Float(), nullable=False),
        sa.Column("prob_implicita_empate", sa.Float(), nullable=False),
        sa.Column("prob_implicita_visitante", sa.Float(), nullable=False),
        sa.Column("fuente", FUENTE_CUOTA_ENUM, nullable=False),
        sa.UniqueConstraint("partido_id", "fuente", name="uq_cuotas_mercado_partido_fuente"),
    )
    op.create_index("ix_cuotas_mercado_partido_id", "cuotas_mercado", ["partido_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_cuotas_mercado_partido_id", table_name="cuotas_mercado")
    op.drop_table("cuotas_mercado")

    op.drop_table("track_record_agregado")

    op.drop_index(
        "ix_evaluaciones_version_modelo_evaluado_en", table_name="evaluaciones_prediccion"
    )
    op.drop_table("evaluaciones_prediccion")

    bind = op.get_bind()
    FUENTE_CUOTA_ENUM.drop(bind, checkfirst=True)
