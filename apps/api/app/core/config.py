from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig", env_prefix="SCI_", case_sensitive=False)

    app_name: str = "Single Riders Comment Intelligence API"
    environment: str = "development"
    database_url: str = "sqlite:///./local.db"
    redis_url: str = "redis://localhost:6379/0"
    allowed_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:3000"])
    worker_mode: str = "inline"
    llm_provider: str = "stub"
    llm_model: str = "single-riders-comment-intelligence-v1"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    github_export_repository: str | None = None
    trello_board_id: str | None = None
    docs_export_path: str = "../../docs/exports"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
