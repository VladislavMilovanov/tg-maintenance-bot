"""Tests for locations API endpoints: hierarchical location tree."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_location_tree_with_auth_returns_200(api_client) -> None:
    """GET /locations/tree with valid auth should return location hierarchy."""

    headers = await _get_auth_headers(api_client)
    response = await api_client.get("/api/v1/locations/tree", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "locations" in payload
    assert len(payload["locations"]) == 1
    node = payload["locations"][0]
    assert node["location_id"] == "loc-1"
    assert node["name"] == "Plant"
    assert node["location_type"] == "plant"
    assert node["status"] == "normal"
    assert node["equipment_count"] == 5
    assert node["children"] == []


@pytest.mark.asyncio
async def test_get_location_tree_without_auth_returns_401(api_client) -> None:
    """GET /locations/tree without auth should return 401."""

    response = await api_client.get("/api/v1/locations/tree")

    assert response.status_code == 401
