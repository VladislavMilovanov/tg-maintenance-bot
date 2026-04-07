"""Tests for sensor group API endpoints: detail view."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_sensor_group_detail_with_auth_returns_200(api_client) -> None:
    """GET /sensor-groups/{id} with valid auth should return sensor group detail."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/sensor-groups/sg-1", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["sensor_group_id"] == "sg-1"
    assert payload["name"] == "Vibration"
    assert payload["group_type"] == "vibration"
    assert payload["status"] == "normal"
    assert payload["image_url"] is None
    assert payload["equipment"]["equipment_id"] == "eq-1"
    assert len(payload["sensors"]) == 1
    assert payload["sensors"][0]["sensor_id"] == "s-1"


@pytest.mark.asyncio
async def test_get_sensor_group_detail_nonexistent_returns_404(api_client) -> None:
    """GET /sensor-groups/nonexistent with valid auth should return 404."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get(
        "/api/v1/sensor-groups/nonexistent", headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_sensor_group_detail_without_auth_returns_401(api_client) -> None:
    """GET /sensor-groups/{id} without auth should return 401."""

    response = await api_client.get("/api/v1/sensor-groups/sg-1")

    assert response.status_code == 401
