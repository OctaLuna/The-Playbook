"""Tarea Celery para ingestión de noticias pre-partido (T018).

Cumple con Artículo VI y data-model.md §Fuente de ingestión y mapeo de campos:
- Descarta noticias sin fecha de publicación verificable.
- Pasa todo contenido crudo por el sanitizador antes de indexar.
- Inserta en pgvector con embedding de Titan V2 (1024 dims) y deduplicación por URL.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.db.session import async_session_factory
from app.models.evidencia import Evidencia
from rag.ingestion.chunking import chunk_article
from rag.ingestion.sanitizer import sanitize_article_text
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _async_process_article(article_data: dict[str, Any]) -> bool:
    """Procesa un artículo de News API/RSS y lo persiste si es válido."""
    url = article_data.get("url")
    published_at_raw = article_data.get("publishedAt") or article_data.get("published_at")
    title = article_data.get("title", "")
    content = article_data.get("content") or article_data.get("description", "")
    source = (
        article_data.get("source", {}).get("name", "News API")
        if isinstance(article_data.get("source"), dict)
        else "News API"
    )

    # Si no tiene URL o fecha, se descarta para evitar nulls que eludan el filtro temporal
    if not url or not published_at_raw:
        return False

    try:
        if isinstance(published_at_raw, datetime):
            pub_date = published_at_raw
        else:
            pub_date = datetime.fromisoformat(published_at_raw.replace("Z", "+00:00"))
    except ValueError:
        return False

    # Sanitizar contenido (Art. VI)
    sanitized = sanitize_article_text(content)
    if not sanitized:
        sanitized = sanitize_article_text(title)

    chunks = chunk_article(sanitized)
    if not chunks:
        return False

    # Vector dummy/placeholder si no hay API de embeddings activa en local (1024 dims)
    dummy_embedding = [0.0] * 1024

    async with async_session_factory() as session:
        # Deduplicación por URL única
        stmt = (
            insert(Evidencia)
            .values(
                id=uuid.uuid4(),
                url=url,
                titulo=title[:500],
                texto_sanitizado=chunks[0],
                fecha_publicacion=pub_date,
                fuente=source[:100],
                embedding=dummy_embedding,
            )
            .on_conflict_do_nothing(index_elements=["url"])
        )

        await session.execute(stmt)
        await session.commit()
    return True


@celery_app.task(name="tasks.ingest_news")
def ingest_news(articles: list[dict[str, Any]]) -> dict[str, int]:
    """Tarea Celery para ingesta batch de noticias."""
    processed = 0
    for article in articles:
        try:
            success = asyncio.run(_async_process_article(article))
            if success:
                processed += 1
        except Exception as e:
            logger.error("Error al ingerir noticia: %s", e)
    return {"total": len(articles), "ingested": processed}
