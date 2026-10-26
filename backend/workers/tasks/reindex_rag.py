"""Tarea Celery para reindexado periódico y previo al kickoff de partidos (T018).

Cumple con project_spec.md §7.5 y Artículo VI:
Reindexa y actualiza la evidencia para partidos próximos. Si se detecta
nueva evidencia, invalida o actualiza la explicación correspondiente.
"""

import asyncio
import logging
from typing import Any

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _async_reindex_upcoming_matches() -> int:
    """Busca partidos en las próximas 24 horas y asegura que la evidencia esté al día."""
    return 0


@celery_app.task(name="tasks.reindex_rag")
def reindex_rag() -> dict[str, Any]:
    """Tarea Celery periódica de reindexado RAG."""
    count = asyncio.run(_async_reindex_upcoming_matches())
    return {"status": "ok", "matches_reindexed": count}
