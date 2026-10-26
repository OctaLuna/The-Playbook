"""Módulo de caché en Redis para explicaciones generadas (T015).

Cumple con project_spec.md §7.5 y RF-006:
Las explicaciones generadas se cachean en Redis y solo se invalidan
si cambia la evidencia subyacente relevante al partido.
"""

import hashlib
import json
import logging
import uuid
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def compute_evidence_hash(evidence_ids: list[uuid.UUID]) -> str:
    """Calcula un hash determinista a partir de los identificadores de evidencia citados."""
    sorted_ids = sorted(str(eid) for eid in evidence_ids)
    raw = ":".join(sorted_ids)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class ExplanationCache:
    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or get_settings().redis_url
        self._redis: aioredis.Redis | None = None

    async def get_client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    def _make_key(self, match_id: uuid.UUID, evidence_hash: str) -> str:
        return f"explanation:{match_id}:{evidence_hash}"

    async def get(self, match_id: uuid.UUID, evidence_hash: str) -> dict[str, Any] | None:
        """Obtiene una explicación en caché si el hash de evidencia coincide."""
        try:
            client = await self.get_client()
            key = self._make_key(match_id, evidence_hash)
            cached_data = await client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Fallo al leer caché de Redis (%s), sirviendo en vivo.", e)
        return None

    async def set(
        self,
        match_id: uuid.UUID,
        evidence_hash: str,
        data: dict[str, Any],
        ttl_seconds: int = 86400,
    ) -> None:
        """Almacena una explicación en caché con TTL de respaldo."""
        try:
            client = await self.get_client()
            key = self._make_key(match_id, evidence_hash)
            await client.setex(key, ttl_seconds, json.dumps(data))
        except Exception as e:
            logger.warning("Fallo al escribir en caché de Redis (%s).", e)
