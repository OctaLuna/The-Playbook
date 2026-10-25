"""crear tablas explicacion y evidencia rag

Revision ID: b332bcde8901
Revises: a221acbb7556
Create Date: 2026-10-25 19:49:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b332bcde8901"
down_revision: str | Sequence[str] | None = "a221acbb7556"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Tabla evidencias
    op.create_table(
        "evidencias",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("titulo", sa.String(length=500), nullable=False),
        sa.Column("texto_sanitizado", sa.Text(), nullable=False),
        sa.Column("fecha_publicacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fuente", sa.String(length=100), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("equipo_relacionado_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("partido_relacionado_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_evidencias_url", "evidencias", ["url"], unique=True)
    op.create_index("ix_evidencias_fecha_publicacion", "evidencias", ["fecha_publicacion"])
    op.create_index(
        "ix_evidencias_embedding_hnsw",
        "evidencias",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    # 2. Tabla explicaciones
    op.create_table(
        "explicaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prediccion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("es_fallback_sin_evidencia", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("shap_features_usadas", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_explicaciones_match_id", "explicaciones", ["match_id"])
    op.create_index("ix_explicaciones_prediccion_id", "explicaciones", ["prediccion_id"], unique=True)

    # 3. Tabla explicacion_evidencias
    op.create_table(
        "explicacion_evidencias",
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
        sa.Column("orden", sa.Integer(), nullable=False, server_default="1"),
    )

    # 4. Tabla preguntas_seguimiento
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
    op.create_index("ix_preguntas_seguimiento_explicacion_id", "preguntas_seguimiento", ["explicacion_id"])


def downgrade() -> None:
    op.drop_table("preguntas_seguimiento")
    op.drop_table("explicacion_evidencias")
    op.drop_table("explicaciones")
    op.drop_table("evidencias")
