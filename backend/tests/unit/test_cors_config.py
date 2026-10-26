import pytest
from pydantic import ValidationError

from app.core.config import Settings


def _settings(cors_origins: str) -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        bedrock_model_id="test-model",
        cors_origins=cors_origins,
    )


def test_cors_origins_are_parsed_as_exact_origins() -> None:
    settings = _settings("http://localhost:3000, https://frontend.example/")

    assert settings.cors_allowed_origins == [
        "http://localhost:3000",
        "https://frontend.example",
    ]


@pytest.mark.parametrize("origins", ["*", "", "https://example.org/path"])
def test_cors_rejects_wildcard_empty_or_path_origins(origins: str) -> None:
    with pytest.raises(ValidationError):
        _settings(origins)
