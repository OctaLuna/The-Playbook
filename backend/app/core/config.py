from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    redis_url: str
    aws_region: str = "us-east-1"
    bedrock_model_id: str
    # T025: Umbral configurable de groundedness/faithfulness que dispara alerta (project_spec §7.6)
    rag_groundedness_threshold: float = 0.80


@lru_cache
def get_settings() -> Settings:
    return Settings()
