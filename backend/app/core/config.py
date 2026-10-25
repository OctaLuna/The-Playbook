from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True
    )

    database_url: str
    redis_url: str
    aws_region: str = "us-east-1"
    bedrock_model_id: str
    news_api_key: str | None = None
    news_rss_feeds: str = ""
    rag_groundedness_alert_threshold: float | None = Field(default=None, ge=0, le=1)

    @property
    def rss_feed_urls(self) -> list[str]:
        return [feed.strip() for feed in self.news_rss_feeds.split(",") if feed.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
