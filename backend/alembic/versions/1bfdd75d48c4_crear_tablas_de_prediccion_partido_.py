"""crear tablas predicciones y calibraciones_historicas (T008, T009)

Revision ID: 1bfdd75d48c4
Revises: 52cb67a25dcc
Create Date: 2026-09-16 16:15:35.459295

Encadenada sobre 52cb67a25dcc (T006/T007, "equipos"/"partidos"), no sobre
a221acbb7556 directamente. Originalmente esta revisión también recreaba
"equipos"/"partidos" — cuando ambas migraciones llegaron a `develop` en
paralelo, eso produjo 2 heads de Alembic y una segunda CREATE TABLE sobre las
mismas tablas. Fix: se le sacó esa parte, ahora solo agrega lo que 52cb67a25dcc
no tenía.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bfdd75d48c4"
down_revision: str | Sequence[str] | None = "52cb67a25dcc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NIVEL_CONFIANZA_ENUM = postgresql.ENUM(
    "alta", "media", "baja", name="nivel_confianza_enum", create_type=False
)
MERCADO_ENUM = postgresql.ENUM(
    "1x2", "over_under_2_5", "btts", name="mercado_enum", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    NIVEL_CONFIANZA_ENUM.create(bind, checkfirst=True)
    MERCADO_ENUM.create(bind, checkfirst=True)

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

    bind = op.get_bind()
    MERCADO_ENUM.drop(bind, checkfirst=True)
    NIVEL_CONFIANZA_ENUM.drop(bind, checkfirst=True)
