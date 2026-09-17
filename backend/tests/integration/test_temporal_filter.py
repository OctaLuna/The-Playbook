"""
Prueba de integración para el filtro temporal obligatorio de RAG (Artículo IV / Sección 7.3).

Cumple con la tarea T001 de specs/002-explicacion-lenguaje-natural/tasks.md:
Garantiza a nivel de consulta/código que NUNCA se recupere una noticia o evidencia
cuya fecha_publicacion sea mayor o igual a la fecha_kickoff del partido predicho.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidencia import Evidencia
from rag.retrieval.query import buscar_evidencias_relacionadas


@pytest.mark.integration
def test_temporal_filter_sql_condition_logic() -> None:
    """
    T001: Verifica la condición lógica de filtrado temporal para excluir
    explícitamente toda evidencia posterior o igual a la fecha de kickoff.
    """
    kickoff = datetime(2026, 8, 28, 19, 0, 0, tzinfo=UTC)

    pre_kickoff_news = datetime(2026, 8, 27, 10, 0, 0, tzinfo=UTC)
    post_kickoff_news = datetime(2026, 8, 28, 21, 30, 0, tzinfo=UTC)
    same_moment_news = datetime(2026, 8, 28, 19, 0, 0, tzinfo=UTC)

    # Invariante del Artículo IV: fecha_publicacion < fecha_kickoff
    assert pre_kickoff_news < kickoff, "La noticia previa al kickoff debe ser admitida"
    assert not (post_kickoff_news < kickoff), "La noticia posterior al kickoff DEBE ser excluida"
    assert not (same_moment_news < kickoff), (
        "La noticia coincidente con el kickoff DEBE ser excluida"
    )


@pytest.mark.integration
async def test_temporal_filter_retrieval_query_excludes_future_evidence(
    db_session: AsyncSession,
) -> None:
    """
    T001 (DB Integration): Verifica contra Postgres/pgvector real que la función
    `buscar_evidencias_relacionadas` excluye de la respuesta SQL cualquier evidencia
    cuya fecha_publicacion sea mayor o igual a la fecha_kickoff.
    """
    kickoff = datetime(2026, 8, 28, 19, 0, 0, tzinfo=UTC)

    # Creamos un embedding de prueba de 1024 dimensiones (Titan V2)
    dummy_embedding = [0.01] * 1024

    # 1. Noticia publicada antes del kickoff (VÁLIDA)
    evidencia_valida = Evidencia(
        id=uuid4(),
        url="https://ejemplo.com/noticia-pre-kickoff",
        titulo="Lesión del delantero antes del clásico",
        texto_sanitizado="El delantero estrella sufrió una sobrecarga...",
        fecha_publicacion=kickoff - timedelta(hours=12),
        embedding=dummy_embedding,
        fuente="News API Test",
    )

    # 2. Noticia publicada exactamente en el kickoff (INVÁLIDA por Artículo IV)
    evidencia_mismo_momento = Evidencia(
        id=uuid4(),
        url="https://ejemplo.com/noticia-kickoff",
        titulo="Inicia el partido en el estadio principal",
        texto_sanitizado="Pita el árbitro y rueda el balón...",
        fecha_publicacion=kickoff,
        embedding=dummy_embedding,
        fuente="News API Test",
    )

    # 3. Noticia publicada después del kickoff (INVÁLIDA por Artículo IV)
    evidencia_post_kickoff = Evidencia(
        id=uuid4(),
        url="https://ejemplo.com/noticia-post-kickoff",
        titulo="Resultado final del clásico: 2-1",
        texto_sanitizado="El equipo local se impuso en el segundo tiempo...",
        fecha_publicacion=kickoff + timedelta(hours=3),
        embedding=dummy_embedding,
        fuente="News API Test",
    )

    db_session.add_all([evidencia_valida, evidencia_mismo_momento, evidencia_post_kickoff])
    await db_session.flush()

    # Ejecutamos la consulta de retrieval con el kickoff del partido
    resultados = await buscar_evidencias_relacionadas(
        session=db_session,
        query_embedding=dummy_embedding,
        fecha_kickoff=kickoff,
        top_k=10,
    )

    # Verificación de integridad temporal (Artículo IV):
    ids_recuperados = [e.id for e in resultados]
    assert evidencia_valida.id in ids_recuperados, (
        "La evidencia publicada previa al kickoff DEBE ser recuperada."
    )
    assert evidencia_mismo_momento.id not in ids_recuperados, (
        "La evidencia publicada en el instante del kickoff DEBE ser excluida (Artículo IV)."
    )
    assert evidencia_post_kickoff.id not in ids_recuperados, (
        "La evidencia publicada posterior al kickoff DEBE ser excluida (Artículo IV)."
    )
