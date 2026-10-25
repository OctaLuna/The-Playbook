"""Prueba de integracin del filtro temporal obligatorio (Artculo IV / RF-002).

La prueba ms crtica del feature: verifica que el retrieval contra la base de datos
aplica estrictamente WHERE fecha_publicacion < fecha_kickoff a nivel SQL, y que
evidencia con fecha posterior al kickoff nunca es recuperada bajo ninguna circunstancia.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models.evidencia import Evidencia
from rag.retrieval.query import query_relevant_evidence


@pytest.mark.asyncio
async def test_filtro_temporal_excluye_evidencia_posterior_al_kickoff(db_session) -> None:
    kickoff = datetime(2026, 9, 15, 18, 0, 0, tzinfo=UTC)
    evidencia_pre_kickoff_id = uuid.uuid4()
    evidencia_post_kickoff_id = uuid.uuid4()

    # Vector dummy de 1024 dimensiones (Titan V2)
    dummy_embedding = [0.01] * 1024

    # 1. Evidencia previa al kickoff (legtima)
    evidencia_pre = Evidencia(
        id=evidencia_pre_kickoff_id,
        url="https://noticias.com/previa-chelsea-arsenal",
        titulo="Previa: Jugador clave en duda para el derbi",
        texto_sanitizado="El jugador clave podra perderse el partido por fatiga muscular.",
        fecha_publicacion=kickoff - timedelta(days=1),
        fuente="News API",
        embedding=dummy_embedding,
    )

    # 2. Evidencia posterior al kickoff (noticia del futuro con el resultado)
    evidencia_post = Evidencia(
        id=evidencia_post_kickoff_id,
        url="https://noticias.com/cronica-chelsea-arsenal",
        titulo="Crnica: Arsenal vence 2-0 con doblete",
        texto_sanitizado="El Arsenal super al rival con comodidad en la segunda parte.",
        fecha_publicacion=kickoff + timedelta(hours=2),
        fuente="News API",
        embedding=dummy_embedding,
    )

    db_session.add_all([evidencia_pre, evidencia_post])
    await db_session.flush()

    # 3. Ejecutar query de retrieval con vector de consulta
    resultados = await query_relevant_evidence(
        session=db_session,
        query_embedding=dummy_embedding,
        kickoff_at=kickoff,
        limit=5,
    )

    # 4. Aserciones constitucionales (Artculo IV):
    ids_recuperados = [ev.id for ev in resultados]
    assert evidencia_pre_kickoff_id in ids_recuperados
    assert evidencia_post_kickoff_id not in ids_recuperados, (
        "Violacin constitucional del Artculo IV: el retrieval devolvi evidencia "
        "con fecha de publicacin posterior al kickoff del partido."
    )
    for ev in resultados:
        assert ev.fecha_publicacion < kickoff
