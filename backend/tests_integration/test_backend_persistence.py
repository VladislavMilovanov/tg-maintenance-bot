"""Integration tests for the SQLAlchemy-backed persistence layer."""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from maintenance_backend.db_urls import to_sqlalchemy_async_url


pytestmark = pytest.mark.asyncio


async def _fetch_scalar(database_url: str, query: str):
    engine = create_async_engine(to_sqlalchemy_async_url(database_url))
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text(query))
            return result.scalar_one()
    finally:
        await engine.dispose()


async def _fetch_one(database_url: str, query: str):
    engine = create_async_engine(to_sqlalchemy_async_url(database_url))
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text(query))
            return result.mappings().one()
    finally:
        await engine.dispose()


async def test_ready_returns_ok(api_client) -> None:
    """Readiness should succeed against the real PostgreSQL-backed runtime."""

    response = await api_client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_assistant_uses_real_equipment_lookup(api_client) -> None:
    """Assistant context validation should read equipment from PostgreSQL."""

    response = await api_client.post(
        "/api/v1/assistant/messages",
        json={
            "channel": "telegram",
            "user": {"external_id": "telegram:123"},
            "message": {"text": "Статус?"},
            "equipment_context": {"equipment_id": "eq-1"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["context_used"] == {
        "equipment_id": "eq-1",
        "sensor_ids": [],
        "sensor_group_ids": [],
        "sources": ["client_payload"],
    }


async def test_create_state_record_persists_to_database(
    api_client,
    integration_database_url: str,
) -> None:
    """Creating a state record should persist the record and its author."""

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "equipment_id": "eq-42",
            "status": "warning",
            "comment": "Температура выше нормы",
            "idempotency_key": "integration-state-1",
            "observed_at": "2026-03-30T10:15:00Z",
            "channel": "telegram",
            "author": {
                "external_id": "telegram:123",
                "display_name": "Ivan",
                "role": "engineer",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["equipment_id"] == "eq-42"
    assert payload["author"] == {
        "external_id": "telegram:123",
        "display_name": "Ivan",
        "role": "engineer",
    }

    record_count = await _fetch_scalar(
        integration_database_url,
        "SELECT COUNT(*) FROM equipment_state_records",
    )
    actor_row = await _fetch_one(
        integration_database_url,
        """
        SELECT external_id, display_name, role
        FROM system_actors
        WHERE external_id = 'telegram:123'
        """,
    )
    assert record_count == 1
    assert dict(actor_row) == {
        "external_id": "telegram:123",
        "display_name": "Ivan",
        "role": "engineer",
    }


async def test_create_state_record_returns_404_for_unknown_equipment(
    api_client,
) -> None:
    """Unknown equipment should still return contract-level 404."""

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "equipment_id": "eq-missing",
            "status": "warning",
            "observed_at": "2026-03-30T10:15:00Z",
            "channel": "telegram",
            "author": {"external_id": "telegram:123"},
        },
    )

    assert response.status_code == 404
    assert response.json()["code"] == "equipment_not_found"


async def test_create_state_record_is_idempotent_for_same_payload(api_client) -> None:
    """The same payload and idempotency key should return the original record."""

    payload = {
        "equipment_id": "eq-42",
        "status": "warning",
        "comment": "Температура выше нормы",
        "idempotency_key": "integration-state-42",
        "observed_at": "2026-03-30T10:15:00Z",
        "channel": "telegram",
        "author": {"external_id": "telegram:123"},
    }

    first_response = await api_client.post(
        "/api/v1/equipment-state-records", json=payload
    )
    second_response = await api_client.post(
        "/api/v1/equipment-state-records", json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()


async def test_create_state_record_returns_409_for_idempotency_conflict(
    api_client,
) -> None:
    """A conflicting payload with the same idempotency key should return 409."""

    first_payload = {
        "equipment_id": "eq-42",
        "status": "warning",
        "comment": "Температура выше нормы",
        "idempotency_key": "integration-state-conflict",
        "observed_at": "2026-03-30T10:15:00Z",
        "channel": "telegram",
        "author": {"external_id": "telegram:123"},
    }
    second_payload = {
        **first_payload,
        "comment": "Комментарий изменился",
    }

    first_response = await api_client.post(
        "/api/v1/equipment-state-records", json=first_payload
    )
    second_response = await api_client.post(
        "/api/v1/equipment-state-records", json=second_payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["code"] == "idempotency_conflict"
