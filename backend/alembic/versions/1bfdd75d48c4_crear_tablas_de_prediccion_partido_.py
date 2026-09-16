"""crear tablas de prediccion partido: partidos equipos predicciones calibraciones

Revision ID: 1bfdd75d48c4
Revises: a221acbb7556
Create Date: 2026-09-16 16:15:35.459295

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bfdd75d48c4"
down_revision: str | Sequence[str] | None = "a221acbb7556"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LIGA_ENUM = postgresql.ENUM(
    "premier_league",
    "laliga",
    "serie_a",
    "bundesliga",
    "ligue_1",
    name="liga_enum",
    create_type=False,
)
ESTADO_PARTIDO_ENUM = postgresql.ENUM(
    "programado",
    "jugado",
    "pospuesto",
    "cancelado",
    name="estado_partido_enum",
    create_type=False,
)
NIVEL_CONFIANZA_ENUM = postgresql.ENUM(
    "alta", "media", "baja", name="nivel_confianza_enum", create_type=False
)
MERCADO_ENUM = postgresql.ENUM(
    "1x2", "over_under_2_5", "btts", name="mercado_enum", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    LIGA_ENUM.create(bind, checkfirst=True)
    ESTADO_PARTIDO_ENUM.create(bind, checkfirst=True)
    NIVEL_CONFIANZA_ENUM.create(bind, checkfirst=True)
    MERCADO_ENUM.create(bind, checkfirst=True)

    op.create_table(
        "equipos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("liga", LIGA_ENUM, nullable=False),
        sa.Column(
            "tiene_historial_suficiente",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.UniqueConstraint("nombre", "liga", name="uq_equipos_nombre_liga"),
    )

    op.create_table(
        "partidos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("liga", LIGA_ENUM, nullable=False),
        sa.Column(
            "equipo_local_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("equipos.id"),
            nullable=False,
        ),
        sa.Column(
            "equipo_visitante_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("equipos.id"),
            nullable=False,
        ),
        sa.Column("fecha_kickoff", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "estado",
            ESTADO_PARTIDO_ENUM,
            nullable=False,
            server_default="programado",
        ),
        sa.Column("goles_local", sa.Integer(), nullable=True),
        sa.Column("goles_visitante", sa.Integer(), nullable=True),
    )
    op.create_index("ix_partidos_liga", "partidos", ["liga"])
    # data-model.md: "la" query del job de Celery (RF-007) — ventana de
    # kickoff + estado programado.
    op.create_index("ix_partidos_fecha_kickoff_estado", "partidos", ["fecha_kickoff", "estado"])

    op.create_table(
        "predicciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "partido_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partidos.id"),
            nullable=False,
        ),
        sa.Column("prob_local", sa.Float(), nullable=False),
        sa.Column("prob_empate", sa.Float(), nullable=False),
        sa.Column("prob_visitante", sa.Float(), nullable=False),
        sa.Column("prob_over_2_5", sa.Float(), nullable=False),
        sa.Column("prob_btts_si", sa.Float(), nullable=False),
        sa.Column("xg_local", sa.Float(), nullable=False),
        sa.Column("xg_visitante", sa.Float(), nullable=False),
        sa.Column("nivel_confianza", NIVEL_CONFIANZA_ENUM, nullable=False),
        sa.Column(
            "head_to_head_disponible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("top_shap_features", sa.JSON(), nullable=False),
        sa.Column("version_modelo", sa.String(128), nullable=False),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("partido_id", name="uq_predicciones_partido_id"),
        sa.CheckConstraint(
            "prob_local + prob_empate + prob_visitante BETWEEN 0.999999 AND 1.000001",
            name="ck_predicciones_1x2_suma_1",
        ),
        sa.CheckConstraint(
            "prob_local BETWEEN 0 AND 1"
            " AND prob_empate BETWEEN 0 AND 1"
            " AND prob_visitante BETWEEN 0 AND 1"
            " AND prob_over_2_5 BETWEEN 0 AND 1"
            " AND prob_btts_si BETWEEN 0 AND 1",
            name="ck_predicciones_probabilidades_en_rango",
        ),
    )

    op.create_table(
        "calibraciones_historicas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mercado", MERCADO_ENUM, nullable=False),
        sa.Column("rango_probabilidad_min", sa.Float(), nullable=False),
        sa.Column("rango_probabilidad_max", sa.Float(), nullable=False),
        sa.Column("precision_empirica", sa.Float(), nullable=False),
        sa.Column("n_observaciones", sa.Integer(), nullable=False),
        sa.Column("version_modelo", sa.String(128), nullable=False),
        sa.UniqueConstraint(
            "mercado",
            "rango_probabilidad_min",
            "version_modelo",
            name="uq_calibracion_mercado_rango_version",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("calibraciones_historicas")
    op.drop_table("predicciones")
    op.drop_index("ix_partidos_fecha_kickoff_estado", table_name="partidos")
    op.drop_index("ix_partidos_liga", table_name="partidos")
    op.drop_table("partidos")
    op.drop_table("equipos")

    bind = op.get_bind()
    MERCADO_ENUM.drop(bind, checkfirst=True)
    NIVEL_CONFIANZA_ENUM.drop(bind, checkfirst=True)
    ESTADO_PARTIDO_ENUM.drop(bind, checkfirst=True)
    LIGA_ENUM.drop(bind, checkfirst=True)
