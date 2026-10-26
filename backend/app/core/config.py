from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True
    )

    database_url: str
    redis_url: str
    aws_region: str = "us-east-1"
    bedrock_model_id: str
    cors_origins: str = "http://localhost:3000"
    news_api_key: str | None = None
    news_rss_feeds: str = ""
    rag_groundedness_alert_threshold: float | None = Field(default=None, ge=0, le=1)

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins or "*" in origins:
            raise ValueError("CORS origins must be a non-empty list of exact origins")
        for origin in origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
                or parsed.username
                or parsed.password
            ):
                raise ValueError(f"Invalid CORS origin: {origin}")
        return ",".join(origins)

    @property
    def rss_feed_urls(self) -> list[str]:
        return [feed.strip() for feed in self.news_rss_feeds.split(",") if feed.strip()]

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
