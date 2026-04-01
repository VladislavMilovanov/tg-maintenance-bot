"""Tests for chat handler backend integration."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from maintenance_bot.backend_client import AssistantApiResult, BackendApiError
from maintenance_bot.handlers.chat import USER_FACING_BACKEND_ERROR, handle_message


def _message(text: str = "Статус?", user_id: int = 123, full_name: str = "Ivan Ivanov"):
    answer = AsyncMock()
    from_user = SimpleNamespace(id=user_id, full_name=full_name, username="ivan")
    return SimpleNamespace(text=text, from_user=from_user, answer=answer)


@pytest.mark.asyncio
async def test_handle_message_uses_backend_client_and_replies() -> None:
    """Handler should proxy the message to backend and answer with backend text."""

    message = _message()
    backend_client = AsyncMock()
    backend_client.create_assistant_message.return_value = AssistantApiResult(
        answer="Ответ из backend",
        conversation_id="conv-1",
    )

    await handle_message(message, backend_client=backend_client)

    backend_client.create_assistant_message.assert_awaited_once_with(
        user_id=123,
        text="Статус?",
        display_name="Ivan Ivanov",
    )
    message.answer.assert_awaited_once_with("Ответ из backend")


@pytest.mark.asyncio
async def test_handle_message_returns_service_error_when_backend_fails() -> None:
    """Handler should hide backend failure details from telegram user."""

    message = _message()
    backend_client = AsyncMock()
    backend_client.create_assistant_message.side_effect = BackendApiError(
        message="Backend request failed.",
        status_code=503,
    )

    await handle_message(message, backend_client=backend_client)

    message.answer.assert_awaited_once_with(USER_FACING_BACKEND_ERROR)
