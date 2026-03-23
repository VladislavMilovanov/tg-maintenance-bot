"""Обработчик текстовых сообщений."""

import logging

from aiogram import Router
from aiogram.types import Message

from maintenance_bot.config import Settings
from maintenance_bot.llm.client import complete

logger = logging.getLogger(__name__)

router = Router(name="chat")

# user_id -> список сообщений {"role": "user"|"assistant", "content": "..."}
_chat_history: dict[int, list[dict[str, str]]] = {}
MAX_HISTORY_MESSAGES = 20


def _get_messages(user_id: int, user_text: str) -> list[dict[str, str]]:
    """Возвращает историю + новое сообщение, ограниченную по длине."""
    if user_id not in _chat_history:
        _chat_history[user_id] = []

    _chat_history[user_id].append({"role": "user", "content": user_text})
    history = _chat_history[user_id][-MAX_HISTORY_MESSAGES:]
    _chat_history[user_id] = history
    return history


def _append_assistant(user_id: int, content: str) -> None:
    """Добавляет ответ ассистента в историю."""
    if user_id not in _chat_history:
        _chat_history[user_id] = []
    _chat_history[user_id].append({"role": "assistant", "content": content})


@router.message()
async def handle_message(message: Message, settings: Settings) -> None:
    """Обработка текстового сообщения от пользователя."""
    if not message.text or not message.from_user:
        return

    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        return

    logger.info("Сообщение от user_id=%s, длина=%d", user_id, len(text))

    messages = _get_messages(user_id, text)

    try:
        response = complete(messages, settings=settings, model=settings.OPENROUTER_MODEL)
        _append_assistant(user_id, response)
        await message.answer(response)
    except Exception as e:
        logger.exception("Ошибка при обработке сообщения: %s", e)
        await message.answer("Произошла ошибка. Попробуйте позже.")
