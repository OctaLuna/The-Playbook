"""Tareas Celery del sistema."""

from workers.tasks.ingest_news import ingest_news
from workers.tasks.reindex_rag import reindex_rag

__all__ = ["ingest_news", "reindex_rag"]
