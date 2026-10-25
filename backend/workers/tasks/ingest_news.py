"""Celery ingestion task for sanitized, deduplicated pre-match news evidence."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.equipo import Equipo
from app.models.evidencia import Evidencia
from rag.generation.client import generar_embedding
from rag.ingestion.chunking import chunk_article
from rag.ingestion.sources import NewsArticle, fetch_news_api, fetch_rss

logger = logging.getLogger(__name__)


def collect_articles(
    teams: list[Equipo], *, api_key: str | None, rss_feeds: list[str]
) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    api_available = bool(api_key)
    if api_key:
        for team in teams:
            league = getattr(team.liga, "value", str(team.liga))
            query = f'"{team.nombre}" {league.replace("_", " ")}'
            try:
                articles.extend(fetch_news_api(query, api_key))
            except Exception:
                logger.warning("News API fetch failed for team %s; trying RSS", team.nombre)
                api_available = False
                break
    if not api_available or not articles:
        for feed_url in rss_feeds:
            try:
                articles.extend(fetch_rss(feed_url))
            except Exception:
                logger.warning("RSS fetch failed for configured feed %s", feed_url, exc_info=True)
                continue
    # Preserve the newest instance while ensuring a single upsert per URL in this run.
    unique: dict[str, NewsArticle] = {}
    for article in articles:
        previous = unique.get(article.url)
        if previous is None or article.published_at >= previous.published_at:
            unique[article.url] = article
    return list(unique.values())


async def upsert_articles(session: AsyncSession, articles: list[NewsArticle]) -> int:
    updated = 0
    for article in articles:
        existing_result = await session.execute(
            select(Evidencia).where(Evidencia.url == article.url)
        )
        evidence = existing_result.scalar_one_or_none()
        changed = evidence is None or any(
            (
                evidence.titulo != article.title,
                evidence.texto_sanitizado != article.content,
                evidence.fecha_publicacion != article.published_at,
                evidence.fuente != article.source,
            )
        )
        if not changed:
            continue
        chunks = chunk_article(article.content, title=article.title)
        vectors = [await generar_embedding(chunk["content"]) for chunk in chunks]
        embedding = [
            sum(vector[index] for vector in vectors) / len(vectors) for index in range(1024)
        ]
        if evidence is None:
            evidence = Evidencia(url=article.url)
            session.add(evidence)
        evidence.titulo = article.title
        evidence.texto_sanitizado = article.content
        evidence.fecha_publicacion = article.published_at.astimezone(UTC)
        evidence.fuente = article.source
        evidence.embedding = embedding
        updated += 1
    await session.flush()
    return updated


async def ingest_news_once() -> int:
    settings = get_settings()
    async with async_session_factory() as session, session.begin():
        result = await session.execute(select(Equipo).order_by(Equipo.nombre))
        articles = collect_articles(
            list(result.scalars()),
            api_key=settings.news_api_key,
            rss_feeds=settings.rss_feed_urls,
        )
        return await upsert_articles(session, articles)


@shared_task(name="workers.tasks.ingest_news.ingest_news")
def ingest_news() -> dict[str, int | str]:
    """Fetch configured sources, sanitize and upsert articles with embeddings."""
    count = asyncio.run(ingest_news_once())
    return {"updated": count, "checked_at": datetime.now(UTC).isoformat()}
