"""crear tablas rag 002: evidencias explicaciones explicacion_evidencia preguntas_seguimiento

Revision ID: 7a8291b09210
Revises: 1bfdd75d48c4
Create Date: 2026-09-16 20:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a8291b09210"
down_revision: str | Sequence[str] | None = "1bfdd75d48c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "evidencias",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("titulo", sa.String(512), nullable=False),
        sa.Column("texto_sanitizado", sa.Text(), nullable=False),
        sa.Column("fecha_publicacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column("fuente", sa.String(128), nullable=False, server_default="News API"),
        sa.Column(
            "equipo_relacionado_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("equipos.id"),
            nullable=True,
        ),
        sa.Column(
            "partido_relacionado_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partidos.id"),
            nullable=True,
        ),
        sa.UniqueConstraint("url", name="uq_evidencias_url"),
    )
    op.create_index("ix_evidencias_url", "evidencias", ["url"])
    op.create_index("ix_evidencias_fecha_publicacion", "evidencias", ["fecha_publicacion"])

    # Indice HNSW para pgvector sobre Evidencia.embedding
    op.create_index(
        "ix_evidencias_embedding",
        "evidencias",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_l2_ops"},
    )

    op.create_table(
        "explicaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "prediccion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("predicciones.id"),
            nullable=False,
        ),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column(
            "es_fallback_sin_evidencia",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("shap_features_usadas", sa.JSON(), nullable=True),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("prediccion_id", name="uq_explicaciones_prediccion_id"),
    )
    op.create_index("ix_explicaciones_prediccion_id", "explicaciones", ["prediccion_id"])

    op.create_table(
        "explicacion_evidencia",
        sa.Column(
            "explicacion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("explicaciones.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "evidencia_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("evidencias.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "preguntas_seguimiento",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "explicacion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("explicaciones.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pregunta", sa.Text(), nullable=False),
        sa.Column("respuesta", sa.Text(), nullable=False),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_preguntas_seguimiento_explicacion_id", "preguntas_seguimiento", ["explicacion_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_preguntas_seguimiento_explicacion_id", table_name="preguntas_seguimiento")
    op.drop_table("preguntas_seguimiento")
    op.drop_table("explicacion_evidencia")
    op.drop_index("ix_explicaciones_prediccion_id", table_name="explicaciones")
    op.drop_table("explicaciones")
    op.drop_index("ix_evidencias_embedding", table_name="evidencias")
    op.drop_index("ix_evidencias_fecha_publicacion", table_name="evidencias")
    op.drop_index("ix_evidencias_url", table_name="evidencias")
    op.drop_table("evidencias")
