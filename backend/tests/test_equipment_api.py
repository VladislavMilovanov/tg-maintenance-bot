"""Tests for equipment API endpoints: list, detail, and history."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_equipment_with_auth_returns_200(api_client) -> None:
    """GET /equipment with valid auth should return paginated equipment list."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/equipment", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["equipment_id"] == "eq-1"
    assert item["name"] == "Turbine 1"
    assert item["current_status"] == "normal"
    assert item["location"]["location_id"] == "loc-1"


@pytest.mark.asyncio
async def test_list_equipment_without_auth_returns_401(api_client) -> None:
    """GET /equipment without auth should return 401."""

    response = await api_client.get("/api/v1/equipment")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_equipment_accepts_filter_params(api_client) -> None:
    """GET /equipment should accept location_id and status query params."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get(
        "/api/v1/equipment?location_id=loc-1&status=normal&limit=10&offset=0",
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_equipment_detail_with_auth_returns_200(api_client) -> None:
    """GET /equipment/{id} with valid auth should return equipment detail."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/equipment/eq-1", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["equipment_id"] == "eq-1"
    assert payload["name"] == "Turbine 1"
    assert payload["equipment_code"] == "GT-001"
    assert payload["current_status"] == "normal"
    assert payload["location"]["location_id"] == "loc-1"
    assert payload["maintenance_progress"] == 0.5
    assert payload["sensor_groups_count"] == 2
    assert payload["top_nodes"] == []


@pytest.mark.asyncio
async def test_get_equipment_detail_nonexistent_returns_404(api_client) -> None:
    """GET /equipment/nonexistent with valid auth should return 404."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/equipment/nonexistent", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_equipment_detail_without_auth_returns_401(api_client) -> None:
    """GET /equipment/{id} without auth should return 401."""

    response = await api_client.get("/api/v1/equipment/eq-1")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_equipment_history_with_auth_returns_200(api_client) -> None:
    """GET /equipment/{id}/history with valid auth should return history list."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/equipment/eq-1/history", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 0
    assert payload["items"] == []


@pytest.mark.asyncio
async def test_get_equipment_history_without_auth_returns_401(api_client) -> None:
    """GET /equipment/{id}/history without auth should return 401."""

    response = await api_client.get("/api/v1/equipment/eq-1/history")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_equipment_history_accepts_pagination_params(api_client) -> None:
    """GET /equipment/{id}/history should accept limit and offset query params."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get(
        "/api/v1/equipment/eq-1/history?limit=5&offset=0", headers=headers
    )

    assert response.status_code == 200
