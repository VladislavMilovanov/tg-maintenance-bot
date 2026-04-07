"""Tests for dashboard API endpoints: plant overview and activity feeds."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_plant_overview_with_auth_returns_200(api_client) -> None:
    """GET /dashboard/plant with valid auth should return plant overview."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/dashboard/plant", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["plant_status"] == "warning"
    assert "status_summary" in payload
    assert "daily_history" in payload
    assert "worst_performers" in payload


@pytest.mark.asyncio
async def test_get_plant_overview_without_auth_returns_401(api_client) -> None:
    """GET /dashboard/plant without auth should return 401."""

    response = await api_client.get("/api/v1/dashboard/plant")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_state_feed_with_auth_returns_200(api_client) -> None:
    """GET /dashboard/state-feed with valid auth should return state change feed."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/dashboard/state-feed", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["equipment_id"] == "eq-1"
    assert item["new_status"] == "warning"


@pytest.mark.asyncio
async def test_get_state_feed_without_auth_returns_401(api_client) -> None:
    """GET /dashboard/state-feed without auth should return 401."""

    response = await api_client.get("/api/v1/dashboard/state-feed")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_action_feed_with_auth_returns_200(api_client) -> None:
    """GET /dashboard/action-feed with valid auth should return action feed."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/dashboard/action-feed", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["record_id"] == "rec-1"
    assert item["equipment_id"] == "eq-1"
    assert item["status"] == "warning"


@pytest.mark.asyncio
async def test_get_action_feed_without_auth_returns_401(api_client) -> None:
    """GET /dashboard/action-feed without auth should return 401."""

    response = await api_client.get("/api/v1/dashboard/action-feed")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_state_feed_respects_limit_and_offset_params(api_client) -> None:
    """GET /dashboard/state-feed should accept limit and offset query params."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get(
        "/api/v1/dashboard/state-feed?limit=5&offset=10", headers=headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_action_feed_respects_limit_and_offset_params(api_client) -> None:
    """GET /dashboard/action-feed should accept limit and offset query params."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get(
        "/api/v1/dashboard/action-feed?limit=5&offset=0", headers=headers
    )

    assert response.status_code == 200
