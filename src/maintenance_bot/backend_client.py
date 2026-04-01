"""Async client for maintenance backend assistant API."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from maintenance_bot.config import Settings

ASSISTANT_MESSAGES_PATH = "/api/v1/assistant/messages"


@dataclass(slots=True)
class AssistantApiResult:
    """Successful assistant API response."""

    answer: str
    conversation_id: str


@dataclass(slots=True)
class BackendApiError(Exception):
    """Normalized backend client error."""

    message: str
    status_code: int | None = None


class BackendClient:
    """Minimal async wrapper around backend HTTP API."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
        )
        self._conversation_ids: dict[int, str] = {}

    @classmethod
    def from_settings(cls, settings: Settings) -> "BackendClient":
        """Create client from bot settings."""
        return cls(
            base_url=settings.BACKEND_URL,
            timeout_seconds=settings.BACKEND_TIMEOUT_SECONDS,
        )

    async def aclose(self) -> None:
        """Close underlying HTTP resources."""
        await self._http.aclose()

    async def create_assistant_message(
        self,
        user_id: int,
        text: str,
        display_name: str | None,
    ) -> AssistantApiResult:
        """Send user message to backend assistant flow."""
        payload = {
            "channel": "telegram",
            "user": {"external_id": f"telegram:{user_id}"},
            "message": {"text": text},
        }
        if display_name:
            payload["user"]["display_name"] = display_name

        conversation_id = self._conversation_ids.get(user_id)
        if conversation_id is not None:
            payload["conversation_id"] = conversation_id

        try:
            response = await self._http.post(ASSISTANT_MESSAGES_PATH, json=payload)
        except httpx.TimeoutException as exc:
            raise BackendApiError("Backend request timed out.") from exc
        except httpx.HTTPError as exc:
            raise BackendApiError("Backend request failed.") from exc

        if response.status_code != httpx.codes.OK:
            raise BackendApiError(
                message="Backend returned an unexpected status.",
                status_code=response.status_code,
            )

        data = response.json()
        result = AssistantApiResult(
            answer=data["answer"],
            conversation_id=data["conversation_id"],
        )
        self._conversation_ids[user_id] = result.conversation_id
        return result
