from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidencia import Evidencia
from rag.ingestion.sources import NewsArticle
from workers.tasks import ingest_news

pytestmark = pytest.mark.integration


async def test_upsert_deduplicates_url_and_reindexes_changed_content(
    db_session: AsyncSession, monkeypatch
) -> None:
    async def fake_embedding(text: str) -> list[float]:
        return [0.1 if "nuevo" in text else 0.01] * 1024

    monkeypatch.setattr(ingest_news, "generar_embedding", fake_embedding)
    url = f"https://news.example/{uuid4()}"
    published = datetime.now(UTC)
    first = NewsArticle("Titular", url, published, "RSS", "Contenido inicial.")
    changed = NewsArticle("Titular actualizado", url, published, "RSS", "Contenido nuevo.")

    assert await ingest_news.upsert_articles(db_session, [first]) == 1
    await db_session.flush()
    assert await ingest_news.upsert_articles(db_session, [changed]) == 1
    await db_session.flush()

    rows = await db_session.execute(select(Evidencia).where(Evidencia.url == url))
    evidence = rows.scalar_one()
    assert evidence.titulo == "Titular actualizado"
    assert evidence.texto_sanitizado == "Contenido nuevo."
    assert evidence.embedding == [0.1] * 1024
