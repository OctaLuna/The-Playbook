import pytest
from pydantic import ValidationError

from app.core.config import Settings
from rag.groundedness import groundedness_alert_triggered


def test_groundedness_alert_is_disabled_when_unset() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        bedrock_model_id="test-model",
    )
    assert settings.rag_groundedness_alert_threshold is None
    assert settings.rss_feed_urls == []


def test_rss_urls_are_read_from_comma_separated_setting() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        bedrock_model_id="test-model",
        news_rss_feeds=" https://rss.example/one, ,https://rss.example/two ",
    )
    assert settings.rss_feed_urls == ["https://rss.example/one", "https://rss.example/two"]


@pytest.mark.parametrize("threshold", [0, 0.25, 1])
def test_groundedness_alert_accepts_threshold_in_unit_interval(threshold: float) -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        bedrock_model_id="test-model",
        rag_groundedness_alert_threshold=threshold,
    )
    assert settings.rag_groundedness_alert_threshold == threshold


@pytest.mark.parametrize("threshold", [-0.01, 1.01])
def test_groundedness_alert_rejects_threshold_outside_unit_interval(threshold: float) -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            redis_url="redis://localhost:6379/0",
            bedrock_model_id="test-model",
            rag_groundedness_alert_threshold=threshold,
        )


def test_groundedness_alert_compares_failure_rate_to_maximum() -> None:
    assert groundedness_alert_triggered(2, 10, 0.1) is True
    assert groundedness_alert_triggered(1, 10, 0.1) is False
    assert groundedness_alert_triggered(10, 10, None) is False
    assert groundedness_alert_triggered(0, 0, 0.1) is False
