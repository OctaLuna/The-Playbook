"""Módulo de retrieval contra pgvector con filtro temporal estricto (T012).

Cumple estrictamente con el Artículo IV de la Constitución y RF-002:
Toda consulta a la base de datos DEBE aplicar a nivel SQL:
`WHERE fecha_publicacion < kickoff_at`
sin excepción, asegurando que ninguna noticia posterior al partido
sea jamás recuperada.
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidencia import Evidencia


async def query_relevant_evidence(
    session: AsyncSession,
    query_embedding: list[float],
    kickoff_at: datetime,
    limit: int = 5,
) -> Sequence[Evidencia]:
    """Recupera la evidencia más relevante para un partido respetando el corte temporal.

    Args:
        session: Sesión asíncrona de base de datos.
        query_embedding: Vector de embeddings de la consulta (1024 dims).
        kickoff_at: Fecha y hora exacta de inicio del partido (UTC).
        limit: Número máximo de evidencias a recuperar.

    Returns:
        Secuencia de objetos Evidencia ordenados por similitud semántica.
    """
    stmt = (
        select(Evidencia)
        .where(Evidencia.fecha_publicacion < kickoff_at)
        .order_by(Evidencia.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )

    result = await session.execute(stmt)
    return result.scalars().all()
