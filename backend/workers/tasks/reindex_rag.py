"""Refresh RAG evidence more often while scheduled matches are approaching."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from celery import shared_task
from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.partido import EstadoPartido, Partido
from workers.tasks.ingest_news import ingest_news_once


async def upcoming_match_exists(now: datetime | None = None) -> bool:
    instant = now or datetime.now(UTC)
    async with async_session_factory() as session:
        result = await session.execute(
            select(Partido.id)
            .where(
                Partido.estado == EstadoPartido.PROGRAMADO,
                Partido.fecha_kickoff >= instant,
                Partido.fecha_kickoff <= instant + timedelta(hours=24),
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None


@shared_task(name="workers.tasks.reindex_rag.reindex_rag")
def reindex_rag() -> dict[str, int | str]:
    """Re-fetch configured sources only when matches enter the 24-hour window."""
    if not asyncio.run(upcoming_match_exists()):
        return {"updated": 0, "status": "no_upcoming_matches"}
    return {"updated": asyncio.run(ingest_news_once()), "status": "reindexed"}
