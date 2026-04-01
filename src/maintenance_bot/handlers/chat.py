"""Обработчик текстовых сообщений."""

import logging

from aiogram import Router
from aiogram.types import Message

from maintenance_bot.backend_client import BackendApiError, BackendClient

logger = logging.getLogger(__name__)

router = Router(name="chat")

USER_FACING_BACKEND_ERROR = "Сервис временно недоступен. Попробуйте позже."


@router.message()
async def handle_message(
    message: Message,
    backend_client: BackendClient,
) -> None:
    """Обработка текстового сообщения от пользователя."""
    if not message.text or not message.from_user:
        return

    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        return

    logger.info("Сообщение от user_id=%s, длина=%d", user_id, len(text))

    try:
        response = await backend_client.create_assistant_message(
            user_id=user_id,
            text=text,
            display_name=message.from_user.full_name or message.from_user.username,
        )
        await message.answer(response.answer)
    except BackendApiError as exc:
        logger.warning(
            "Backend error for user_id=%s status_code=%s: %s",
            user_id,
            exc.status_code,
            exc.message,
        )
        await message.answer(USER_FACING_BACKEND_ERROR)
    except Exception:
        logger.exception(
            "Unexpected error while processing message for user_id=%s", user_id
        )
        await message.answer(USER_FACING_BACKEND_ERROR)
