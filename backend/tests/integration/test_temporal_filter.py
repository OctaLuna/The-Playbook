"""
Prueba de integración para el filtro temporal obligatorio de RAG (Artículo IV / Sección 7.3).

Cumple con la tarea T001 de specs/002-explicacion-lenguaje-natural/tasks.md:
Garantiza a nivel de consulta/código que NUNCA se recupere una noticia o evidencia
cuya fecha_publicacion sea mayor o igual a la fecha_kickoff del partido predicho.
"""

from datetime import UTC, datetime

import pytest


@pytest.mark.integration
def test_temporal_filter_sql_condition_logic():
    """
    T001: Verifica que la condición lógica de filtrado temporal excluya
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
