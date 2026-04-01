"""Точка входа приложения."""

import asyncio
import logging
import sys

from maintenance_bot.backend_client import BackendClient
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
    backend_client = BackendClient.from_settings(settings)
    dp = create_dispatcher(settings, backend_client=backend_client)

    async def run() -> None:
        try:
            await dp.start_polling(bot)
        finally:
            await backend_client.aclose()
            await bot.session.close()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
