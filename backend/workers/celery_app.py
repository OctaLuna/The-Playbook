"""Celery application and periodic prediction-generation schedule."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("the_playbook", broker=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=(
        "workers.tasks.generate_predictions",
        "workers.tasks.ingest_news",
        "workers.tasks.reindex_rag",
    ),
    beat_schedule={
        "generate-predictions-every-hour": {
            "task": "workers.tasks.generate_predictions.generate_predictions",
            "schedule": crontab(minute=0),
        },
        "ingest-news-every-six-hours": {
            "task": "workers.tasks.ingest_news.ingest_news",
            "schedule": crontab(minute=15, hour="*/6"),
        },
        "reindex-rag-every-15-minutes": {
            "task": "workers.tasks.reindex_rag.reindex_rag",
            "schedule": crontab(minute="*/15"),
        },
    },
)
