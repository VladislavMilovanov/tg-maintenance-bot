"""Конфигурация из переменных окружения."""

from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    TELEGRAM_BOT_TOKEN: str = Field(..., min_length=1)
    BACKEND_URL: str = "http://127.0.0.1:8000"
    BACKEND_TIMEOUT_SECONDS: float = Field(default=20, gt=0)
    LOG_LEVEL: str = "INFO"
    EQUIPMENT_DATA_PATH: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    WHISPER_MODEL: str = "whisper-1"
