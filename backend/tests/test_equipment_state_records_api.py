"""Baseline API tests for manual equipment state records."""

import pytest


@pytest.mark.asyncio
async def test_create_equipment_state_record_returns_created(api_client) -> None:
    """State record endpoint should create and echo normalized payload."""

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "equipment_id": "eq-42",
            "status": "warning",
            "comment": "Температура выше нормы",
            "idempotency_key": "state-1",
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
    assert payload["record_id"].startswith("state-record-")
    assert payload["equipment_id"] == "eq-42"
    assert payload["status"] == "warning"
    assert payload["comment"] == "Температура выше нормы"
    assert payload["observed_at"] == "2026-03-30T10:15:00Z"
    assert payload["channel"] == "telegram"
    assert payload["author"] == {
        "external_id": "telegram:123",
        "display_name": "Ivan",
        "role": "engineer",
    }
    assert payload["created_at"].endswith("Z")


@pytest.mark.asyncio
async def test_create_equipment_state_record_returns_404_for_unknown_equipment(
    api_client,
) -> None:
    """Unknown equipment should produce contract-level 404 response."""

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
    assert response.json() == {
        "code": "equipment_not_found",
        "message": "Equipment was not found.",
        "details": None,
        "trace_id": None,
    }


@pytest.mark.asyncio
async def test_create_equipment_state_record_is_idempotent_for_same_payload(
    api_client,
) -> None:
    """Reusing the same idempotency key and payload should return the original record."""

    payload = {
        "equipment_id": "eq-42",
        "status": "warning",
        "comment": "Температура выше нормы",
        "idempotency_key": "state-42",
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


@pytest.mark.asyncio
async def test_create_equipment_state_record_retry_returns_original_when_equipment_disappears(
    app,
    api_client,
) -> None:
    """Idempotent retry should return the stored record even if equipment vanishes later."""

    payload = {
        "equipment_id": "eq-42",
        "status": "warning",
        "comment": "Температура выше нормы",
        "idempotency_key": "state-disappearing-equipment",
        "observed_at": "2026-03-30T10:15:00Z",
        "channel": "telegram",
        "author": {"external_id": "telegram:123"},
    }

    first_response = await api_client.post(
        "/api/v1/equipment-state-records", json=payload
    )
    app.state.equipment_repository.equipment_ids.remove("eq-42")
    second_response = await api_client.post(
        "/api/v1/equipment-state-records", json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()


@pytest.mark.asyncio
async def test_create_equipment_state_record_returns_409_for_idempotency_conflict(
    api_client,
) -> None:
    """Reusing the same idempotency key with a different payload should fail."""

    first_payload = {
        "equipment_id": "eq-42",
        "status": "warning",
        "comment": "Температура выше нормы",
        "idempotency_key": "state-42",
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
    assert second_response.json() == {
        "code": "idempotency_conflict",
        "message": "Idempotency key conflicts with an existing record.",
        "details": None,
        "trace_id": None,
    }


@pytest.mark.asyncio
async def test_create_equipment_state_record_rejects_missing_required_field(
    api_client,
) -> None:
    """State record endpoint should return unified validation payload."""

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "status": "warning",
            "observed_at": "2026-03-30T10:15:00Z",
            "channel": "telegram",
            "author": {"external_id": "telegram:123"},
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": [{"field": "equipment_id", "issue": "Field required"}],
        "trace_id": None,
    }


@pytest.mark.asyncio
async def test_create_equipment_state_record_rejects_invalid_status_enum(
    api_client,
) -> None:
    """State record endpoint should reject unsupported status values."""

    response = await api_client.post(
        "/api/v1/equipment-state-records",
        json={
            "equipment_id": "eq-42",
            "status": "broken",
            "observed_at": "2026-03-30T10:15:00Z",
            "channel": "telegram",
            "author": {"external_id": "telegram:123"},
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert payload["message"] == "Request validation failed."
    assert payload["trace_id"] is None
    assert payload["details"] == [
        {
            "field": "status",
            "issue": "Input should be 'normal', 'warning', 'critical' or 'unknown'",
        }
    ]
