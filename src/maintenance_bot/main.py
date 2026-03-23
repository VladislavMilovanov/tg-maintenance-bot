"""Точка входа приложения."""

import asyncio
import logging
import sys

from maintenance_bot.bot import create_bot, create_dispatcher
from maintenance_bot.config import Settings


def main() -> None:
    """Запуск бота."""
    settings = Settings()

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    bot = create_bot(settings)
    dp = create_dispatcher(settings)

    async def run() -> None:
        await dp.start_polling(bot)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
