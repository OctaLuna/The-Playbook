"""Redis cache for generated explanation text, keyed by its exact evidence context."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import TYPE_CHECKING
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

if TYPE_CHECKING:
    from app.models.evidencia import Evidencia

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 24 * 60 * 60


def evidence_fingerprint(
    evidence: list[Evidencia], shap_features: dict[str, float] | None
) -> str:
    """Hash exactly the evidence and SHAP inputs that can affect generated text."""
    serialized = json.dumps(
        {
            "evidence": [
                {
                    "id": str(item.id),
                    "title": item.titulo,
                    "url": item.url,
                    "published_at": item.fecha_publicacion.isoformat(),
                    "text": item.texto_sanitizado,
                }
                for item in evidence
            ],
            "shap": shap_features or {},
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def _cache_key(prediction_id: UUID, fingerprint: str) -> str:
    return f"rag:explanation:{prediction_id}:{fingerprint}"


async def get_cached_explanation(prediction_id: UUID, fingerprint: str) -> str | None:
    client = _redis_client()
    try:
        return await client.get(_cache_key(prediction_id, fingerprint))
    except RedisError:
        logger.warning("Redis unavailable while reading explanation cache", exc_info=True)
        return None
    finally:
        await client.aclose()


async def cache_explanation(prediction_id: UUID, fingerprint: str, text: str) -> None:
    client = _redis_client()
    try:
        await client.set(
            _cache_key(prediction_id, fingerprint), text, ex=CACHE_TTL_SECONDS
        )
    except RedisError:
        logger.warning("Redis unavailable while writing explanation cache", exc_info=True)
    finally:
        await client.aclose()
