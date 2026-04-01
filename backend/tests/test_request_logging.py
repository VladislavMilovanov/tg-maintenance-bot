"""Tests for privacy-safe backend request logging."""

import logging

import pytest


@pytest.mark.asyncio
async def test_assistant_request_logging_omits_message_text_and_logs_sizes(
    api_client,
    caplog,
) -> None:
    """Assistant request logs should include chat_id and sizes but not message text."""

    caplog.set_level(logging.INFO, logger="maintenance_backend.app")

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123456"},
            "message": {"text": "Секретный текст проверки логов"},
        },
    )

    assert response.status_code == 200
    handled_logs = [
        record.message
        for record in caplog.records
        if "Handled request" in record.message
    ]
    assert handled_logs
    last_log = handled_logs[-1]
    assert "chat_id=123456" in last_log
    assert "request_bytes=" in last_log
    assert "response_bytes=" in last_log
    assert "Секретный текст проверки логов" not in last_log


@pytest.mark.asyncio
async def test_state_record_logging_uses_author_external_id_as_chat_id(
    api_client,
    caplog,
) -> None:
    """State-record logging should derive chat_id from author external_id."""

    caplog.set_level(logging.INFO, logger="maintenance_backend.app")

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "equipment_id": "eq-42",
            "status": "warning",
            "observed_at": "2026-03-30T10:15:00Z",
            "channel": "telegram",
            "author": {"external_id": "telegram:987654"},
        },
    )

    assert response.status_code == 201
    handled_logs = [
        record.message
        for record in caplog.records
        if "Handled request" in record.message
    ]
    assert handled_logs
    assert "chat_id=987654" in handled_logs[-1]
