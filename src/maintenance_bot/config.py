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
    OPENROUTER_API_KEY: str = Field(..., min_length=1)
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"
    LOG_LEVEL: str = "INFO"
    EQUIPMENT_DATA_PATH: str | None = None
