"""
Módulo de recuperación (retrieval) de evidencias en pgvector.

Cumple con el Artículo IV de la Constitución y la tarea T012:
- INVARIANTE: Consulta a pgvector con filtro estricto a nivel SQL:
  WHERE fecha_publicacion < fecha_kickoff.
- Garantiza que NUNCA se recupere o cite evidencia publicada en o después del kickoff.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidencia import Evidencia


async def buscar_evidencias_relacionadas(
    session: AsyncSession,
    query_embedding: list[float],
    fecha_kickoff: datetime,
    equipo_id: UUID | None = None,
    partido_id: UUID | None = None,
    top_k: int = 5,
) -> list[Evidencia]:
    """
    Busca las evidencias más relevantes en la base de datos pgvector.

    Garantía de Integridad Temporal (Artículo IV):
    La consulta incluye incondicionalmente la cláusula:
    WHERE fecha_publicacion < fecha_kickoff

    Args:
        session: Sesión asíncrona de SQLAlchemy.
        query_embedding: Vector de embedding de la consulta (1024 floats para Titan V2).
        fecha_kickoff: Timestamp UTC del kickoff del partido a predecir/explicar.
        equipo_id: ID opcional del equipo para filtrar evidencias relacionadas.
        partido_id: ID opcional del partido para filtrar evidencias asociadas.
        top_k: Número máximo de evidencias a retornar (default 5).

    Returns:
        Lista de instancias de `Evidencia` que satisfacen estrictamente el filtro temporal,
        ordenadas por distancia L2 vectorial ascendente.
    """
    # INVARIANTE CONSTITUCIONAL (Artículo IV / Sección 7.3 del spec):
    # La restricción fecha_publicacion < fecha_kickoff se aplica directamente en la consulta SQL.
    stmt = select(Evidencia).where(Evidencia.fecha_publicacion < fecha_kickoff)

    if partido_id is not None:
        stmt = stmt.where(
            (Evidencia.partido_relacionado_id == partido_id)
            | (Evidencia.partido_relacionado_id.is_(None))
        )

    if equipo_id is not None:
        stmt = stmt.where(
            (Evidencia.equipo_relacionado_id == equipo_id)
            | (Evidencia.equipo_relacionado_id.is_(None))
        )

    # Ordenamiento por distancia vectorial L2 usando pgvector
    stmt = stmt.order_by(Evidencia.embedding.l2_distance(query_embedding)).limit(top_k)

    result = await session.execute(stmt)
    return list(result.scalars().all())
