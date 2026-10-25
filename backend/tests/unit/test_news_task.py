from datetime import UTC, datetime
from types import SimpleNamespace

from rag.ingestion.sources import NewsArticle
from workers.tasks import ingest_news


def _article(url: str, title: str = "Titular") -> NewsArticle:
    return NewsArticle(
        title=title,
        url=url,
        published_at=datetime(2026, 10, 25, tzinfo=UTC),
        source="Sports RSS",
        content="Texto ya sanitizado.",
    )


def test_collect_articles_falls_back_to_rss_and_deduplicates(monkeypatch) -> None:
    monkeypatch.setattr(
        ingest_news,
        "fetch_news_api",
        lambda *_: (_ for _ in ()).throw(TimeoutError("News API unavailable")),
    )
    monkeypatch.setattr(
        ingest_news,
        "fetch_rss",
        lambda _: [
            _article("https://news.example/a"),
            _article("https://news.example/a", "Updated"),
        ],
    )
    team = SimpleNamespace(nombre="Arsenal", liga=SimpleNamespace(value="premier_league"))

    articles = ingest_news.collect_articles(
        [team], api_key="test", rss_feeds=["https://rss.example"]
    )

    assert len(articles) == 1
    assert articles[0].title == "Updated"
