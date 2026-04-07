"""Baseline API tests for the assistant scenario."""

import pytest

from maintenance_backend.schemas.assistant import (
    AssistantMessageRequest,
)
from maintenance_backend.services.assistant import (
    DefaultAssistantService,
    FALLBACK_ANSWER,
)


@pytest.mark.asyncio
async def test_assistant_message_returns_gateway_response(api_client) -> None:
    """Assistant endpoint should return gateway-backed 200 response."""

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "message": {"text": "Что с компрессором К-12?"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].endswith(":Что с компрессором К-12?")
    assert payload["conversation_id"].startswith("conv-")
    assert payload["context_used"] is None
    assert payload["meta"] == {"fallback_used": False, "trace_id": None}


@pytest.mark.asyncio
async def test_assistant_message_reuses_known_conversation_id(app, api_client) -> None:
    """Known conversation IDs should be reused instead of regenerated."""

    conversation_id = await app.state.conversation_store.resolve(None)
    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "conversation_id": conversation_id,
            "message": {"text": "Статус?"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] == conversation_id
    assert payload["meta"] == {"fallback_used": False, "trace_id": None}


@pytest.mark.asyncio
async def test_assistant_message_generates_new_conversation_for_unknown_id(
    api_client,
) -> None:
    """Unknown conversation IDs should be replaced with a new backend-owned ID."""

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "conversation_id": "conv-unknown",
            "message": {"text": "Статус?"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] != "conv-unknown"
    assert payload["conversation_id"].startswith("conv-")


@pytest.mark.asyncio
async def test_assistant_message_returns_fallback_when_gateway_is_unavailable(
    app,
    api_client,
) -> None:
    """Assistant endpoint should degrade to fallback response on gateway failure."""

    app.state.assistant_gateway.mode = "fail"

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "conversation_id": "conv-001",
            "message": {"text": "Статус?"},
            "equipment_context": {"equipment_id": "eq-1"},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": FALLBACK_ANSWER,
        "conversation_id": response.json()["conversation_id"],
        "context_used": {
            "equipment_id": "eq-1",
            "sensor_ids": [],
            "sensor_group_ids": [],
            "sources": ["client_payload"],
        },
        "meta": {"fallback_used": True, "trace_id": None},
    }


@pytest.mark.asyncio
async def test_assistant_message_returns_503_when_fallback_cannot_be_built(
    app,
    api_client,
) -> None:
    """Assistant endpoint should return 503 if both gateway and fallback fail."""

    app.state.assistant_gateway.mode = "fail_hard"

    class BrokenFallbackAssistantService(DefaultAssistantService):
        def _build_fallback_answer(self, _: AssistantMessageRequest) -> str:
            raise RuntimeError("fallback failed")

    app.state.assistant_service = BrokenFallbackAssistantService(
        gateway=app.state.assistant_gateway,
        equipment_repository=app.state.equipment_repository,
        conversation_store=app.state.conversation_store,
    )

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "message": {"text": "Статус?"},
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "code": "assistant_unavailable",
        "message": "Assistant is temporarily unavailable.",
        "details": None,
        "trace_id": None,
    }


@pytest.mark.asyncio
async def test_assistant_message_ignores_unknown_equipment_context(api_client) -> None:
    """Assistant endpoint should succeed with null context when equipment_id is unknown."""

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "message": {"text": "Статус?"},
            "equipment_context": {"equipment_id": "eq-missing"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["context_used"] is None
