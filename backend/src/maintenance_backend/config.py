"""Backend configuration loaded from environment variables."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_local_env() -> None:
    """Load local env files for both root-level and backend-only workflows."""

    for env_path in (Path(".env"), Path("backend/.env")):
        load_dotenv(env_path, override=False)


class Settings(BaseSettings):
    """Runtime settings for backend service."""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="dev", alias="BACKEND_APP_ENV")
    host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    port: int = Field(default=8000, alias="BACKEND_PORT", ge=1, le=65535)
    log_level: str = Field(default="INFO", alias="BACKEND_LOG_LEVEL")
    openrouter_api_key: str | None = Field(
        default=None, alias="BACKEND_OPENROUTER_API_KEY"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="BACKEND_OPENROUTER_BASE_URL",
    )
    openrouter_model: str = Field(
        default="nvidia/nemotron-3-super-120b-a12b:free",
        alias="BACKEND_OPENROUTER_MODEL",
    )
    openrouter_timeout_seconds: float = Field(
        default=20.0,
        alias="BACKEND_OPENROUTER_TIMEOUT_SECONDS",
        gt=0,
    )
    openrouter_system_prompt: str = Field(
        default=(
            "Ты помощник по мониторингу оборудования. Отвечай кратко, по-русски, "
            "опираясь только на переданный контекст и не выдумывай факты."
        ),
        alias="BACKEND_OPENROUTER_SYSTEM_PROMPT",
    )
    database_url: str = Field(alias="BACKEND_DATABASE_URL")
    conversation_ttl_seconds: int = Field(
        default=1800,
        alias="BACKEND_CONVERSATION_TTL_SECONDS",
        ge=1,
    )
