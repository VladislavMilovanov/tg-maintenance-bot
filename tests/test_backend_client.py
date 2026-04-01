"""Tests for telegram bot backend client."""

import json

import httpx
import pytest

from maintenance_bot.backend_client import BackendApiError, BackendClient


def _build_test_client(transport: httpx.MockTransport) -> BackendClient:
    client = BackendClient(base_url="http://testserver", timeout_seconds=5)
    client._http = httpx.AsyncClient(  # noqa: SLF001
        base_url="http://testserver",
        timeout=5,
        transport=transport,
    )
    return client


@pytest.mark.asyncio
async def test_backend_client_sends_message_and_persists_conversation_id() -> None:
    """Conversation ID should be reused after first successful request."""

    captured_requests: list[dict[str, object]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(json.loads(request.content.decode()))
        payload = {
            "answer": "ok",
            "conversation_id": f"conv-{len(captured_requests)}",
        }
        return httpx.Response(status_code=200, json=payload)

    client = _build_test_client(httpx.MockTransport(handler))

    try:
        first = await client.create_assistant_message(123, "Привет", "User Name")
        second = await client.create_assistant_message(123, "Статус?", "User Name")
    finally:
        await client.aclose()

    assert first.answer == "ok"
    assert first.conversation_id == "conv-1"
    assert second.conversation_id == "conv-2"
    assert captured_requests[0]["user"] == {
        "external_id": "telegram:123",
        "display_name": "User Name",
    }
    assert "conversation_id" not in captured_requests[0]
    assert captured_requests[1]["conversation_id"] == "conv-1"


@pytest.mark.asyncio
async def test_backend_client_raises_normalized_error_on_timeout() -> None:
    """Timeouts should be mapped to BackendApiError."""

    async def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom")

    client = _build_test_client(httpx.MockTransport(handler))

    try:
        with pytest.raises(BackendApiError) as exc_info:
            await client.create_assistant_message(123, "Привет", None)
    finally:
        await client.aclose()

    assert exc_info.value.status_code is None
    assert exc_info.value.message == "Backend request timed out."


@pytest.mark.asyncio
async def test_backend_client_raises_normalized_error_on_non_200() -> None:
    """Unexpected backend status should be normalized."""

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=503, json={"code": "assistant_unavailable"})

    client = _build_test_client(httpx.MockTransport(handler))

    try:
        with pytest.raises(BackendApiError) as exc_info:
            await client.create_assistant_message(123, "Привет", None)
    finally:
        await client.aclose()

    assert exc_info.value.status_code == 503
    assert exc_info.value.message == "Backend returned an unexpected status."
