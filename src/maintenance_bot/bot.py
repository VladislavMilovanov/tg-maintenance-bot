"""Настройка aiogram Bot и Dispatcher."""

from aiogram import Bot, Dispatcher

from maintenance_bot.config import Settings
from maintenance_bot.handlers import chat_router


def create_bot(settings: Settings) -> Bot:
    """Создание экземпляра Bot."""
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)


def create_dispatcher(settings: Settings) -> Dispatcher:
    """Создание Dispatcher с роутерами."""
    dp = Dispatcher()
    dp["settings"] = settings
    dp.include_router(chat_router)
    return dp
