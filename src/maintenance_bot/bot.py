"""Настройка aiogram Bot и Dispatcher."""

from aiogram import Bot, Dispatcher

from maintenance_bot.backend_client import BackendClient
from maintenance_bot.config import Settings
from maintenance_bot.handlers import chat_router


def create_bot(settings: Settings) -> Bot:
    """Создание экземпляра Bot."""
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)


def create_dispatcher(settings: Settings, backend_client: BackendClient) -> Dispatcher:
    """Создание Dispatcher с роутерами."""
    dp = Dispatcher()
    dp["settings"] = settings
    dp["backend_client"] = backend_client
    dp.include_router(chat_router)
    return dp
