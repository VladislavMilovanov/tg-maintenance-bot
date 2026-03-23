"""OpenRouter-клиент (OpenAI-совместимый API)."""

import logging

from openai import OpenAI

from maintenance_bot.config import Settings
from maintenance_bot.llm.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "openai/gpt-3.5-turbo"
ERROR_MESSAGE = "Не удалось получить ответ. Попробуйте позже."


def complete(
    messages: list[dict[str, str]],
    *,
    settings: Settings,
    model: str = DEFAULT_MODEL,
) -> str:
    """Запрос к LLM через OpenRouter.

    Args:
        messages: Список сообщений [{"role": "user"|"assistant"|"system", "content": "..."}]
        settings: Конфигурация с API-ключом
        model: Модель OpenRouter (по умолчанию gpt-3.5-turbo)

    Returns:
        Текст ответа ассистента или сообщение об ошибке
    """
    client = OpenAI(
        base_url=settings.OPENROUTER_BASE_URL,
        api_key=settings.OPENROUTER_API_KEY,
    )

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    logger.info("Вызов LLM, сообщений в контексте: %d", len(full_messages))

    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
        )
        content = response.choices[0].message.content
        return content or ""
    except Exception as e:
        logger.exception("Ошибка вызова LLM: %s", e)
        return ERROR_MESSAGE
