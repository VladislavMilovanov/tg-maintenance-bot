"""LLM gateway abstractions for assistant flow."""

from __future__ import annotations

from typing import Protocol

from openai import AsyncOpenAI

from maintenance_backend.schemas.assistant import AssistantMessageRequest


class AssistantGatewayError(Exception):
    """Raised when assistant gateway cannot produce a valid answer."""


class AssistantGateway(Protocol):
    """Assistant interpretation gateway contract."""

    async def generate_answer(
        self,
        request: AssistantMessageRequest,
        *,
        conversation_id: str,
    ) -> str: ...

    async def close(self) -> None: ...


class OpenRouterAssistantGateway:
    """OpenAI-compatible gateway targeting OpenRouter."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout_seconds: float,
        system_prompt: str,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._system_prompt = system_prompt
        self._client = AsyncOpenAI(
            api_key=api_key or "missing",
            base_url=base_url,
            timeout=timeout_seconds,
        )

    async def generate_answer(
        self,
        request: AssistantMessageRequest,
        *,
        conversation_id: str,
    ) -> str:
        if not self._api_key:
            raise AssistantGatewayError("OpenRouter API key is not configured.")

        prompt = self._build_user_prompt(request, conversation_id=conversation_id)
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as exc:  # pragma: no cover - vendor exception mapping
            raise AssistantGatewayError("OpenRouter request failed.") from exc

        answer = completion.choices[0].message.content if completion.choices else None
        if not isinstance(answer, str) or not answer.strip():
            raise AssistantGatewayError("OpenRouter returned an empty answer.")
        return answer.strip()

    def _build_user_prompt(
        self,
        request: AssistantMessageRequest,
        *,
        conversation_id: str,
    ) -> str:
        lines = [
            f"Conversation ID: {conversation_id}",
            f"Channel: {request.channel.value}",
            f"User: {request.user.external_id}",
            f"Message: {request.message.text.strip()}",
        ]
        if request.equipment_context is not None:
            lines.append(f"Equipment ID: {request.equipment_context.equipment_id}")
            if request.equipment_context.sensor_ids:
                lines.append(
                    f"Sensor IDs: {', '.join(request.equipment_context.sensor_ids)}"
                )
            if request.equipment_context.sensor_group_ids:
                lines.append(
                    "Sensor group IDs: "
                    + ", ".join(request.equipment_context.sensor_group_ids)
                )
        return "\n".join(lines)

    async def close(self) -> None:
        """Close underlying HTTP client resources."""

        await self._client.close()
