"""Real Redis test for relevant-context invalidation of explanation output."""

import os
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from redis.asyncio import Redis
from redis.exceptions import RedisError

from rag.generation import cache

pytestmark = pytest.mark.integration


async def test_explanation_cache_hits_and_invalidates_when_evidence_changes(
    monkeypatch,
) -> None:
    redis_url = os.getenv("PLAYBOOK_TEST_REDIS_URL", "redis://localhost:56379/0")
    probe = Redis.from_url(redis_url, decode_responses=True)
    try:
        await probe.ping()
    except RedisError:
        pytest.skip("Redis integration service is not available")
    finally:
        await probe.aclose()

    monkeypatch.setattr(
        cache,
        "_redis_client",
        lambda: Redis.from_url(redis_url, decode_responses=True),
    )
    prediction_id = uuid4()
    evidence = SimpleNamespace(
        id=uuid4(),
        titulo="Titular",
        url="https://news.example/item",
        fecha_publicacion=datetime(2026, 10, 24, tzinfo=UTC),
        texto_sanitizado="Contenido de la evidencia",
    )
    original_fingerprint = cache.evidence_fingerprint([evidence], {"forma_local": 0.3})

    assert await cache.get_cached_explanation(prediction_id, original_fingerprint) is None
    await cache.cache_explanation(
        prediction_id, original_fingerprint, "Explicación respaldada por esta noticia."
    )
    assert (
        await cache.get_cached_explanation(prediction_id, original_fingerprint)
        == "Explicación respaldada por esta noticia."
    )

    evidence.texto_sanitizado = "Contenido corregido de la misma evidencia"
    changed_fingerprint = cache.evidence_fingerprint([evidence], {"forma_local": 0.3})
    assert changed_fingerprint != original_fingerprint
    assert await cache.get_cached_explanation(prediction_id, changed_fingerprint) is None
