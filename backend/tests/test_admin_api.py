"""Tests for admin API endpoints: dashboard KPIs, client list, and event feed."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _get_admin_headers(api_client) -> dict[str, str]:
    return await _get_auth_headers(api_client, username="admin")


@pytest.mark.asyncio
async def test_get_admin_dashboard_with_admin_auth_returns_200(api_client) -> None:
    """GET /admin/dashboard with admin auth should return KPIs and charts."""

    headers = await _get_admin_headers(api_client)
    response = await api_client.get("/api/v1/admin/dashboard", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "kpis" in payload
    assert "activity_chart" in payload
    assert "progress_matrix" in payload
    kpis = payload["kpis"]
    assert kpis["total_equipment"] == 5
    assert kpis["critical_count"] == 1
    assert kpis["warning_count"] == 1
    assert kpis["clients_count"] == 3


@pytest.mark.asyncio
async def test_get_admin_dashboard_with_non_admin_returns_403(api_client) -> None:
    """GET /admin/dashboard with regular user auth should return 403."""

    headers = await _get_auth_headers(api_client, username="regularuser")
    response = await api_client.get("/api/v1/admin/dashboard", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_admin_dashboard_without_auth_returns_401(api_client) -> None:
    """GET /admin/dashboard without auth should return 401."""

    response = await api_client.get("/api/v1/admin/dashboard")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_clients_with_admin_auth_returns_200(api_client) -> None:
    """GET /admin/clients with admin auth should return paginated client list."""

    headers = await _get_admin_headers(api_client)
    response = await api_client.get("/api/v1/admin/clients", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 1
    client = payload["items"][0]
    assert client["actor_id"] == "a-1"
    assert client["external_id"] == "web:admin"
    assert client["display_name"] == "Admin"
    assert client["role"] == "admin"
    assert client["equipment_count"] == 3


@pytest.mark.asyncio
async def test_list_clients_with_non_admin_returns_403(api_client) -> None:
    """GET /admin/clients with regular user auth should return 403."""

    headers = await _get_auth_headers(api_client, username="regularuser")
    response = await api_client.get("/api/v1/admin/clients", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_clients_without_auth_returns_401(api_client) -> None:
    """GET /admin/clients without auth should return 401."""

    response = await api_client.get("/api/v1/admin/clients")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_events_with_admin_auth_returns_200(api_client) -> None:
    """GET /admin/events with admin auth should return paginated event feed."""

    headers = await _get_admin_headers(api_client)
    response = await api_client.get("/api/v1/admin/events", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert payload["total"] == 1
    event = payload["items"][0]
    assert event["event_type"] == "state_change"
    assert event["equipment_id"] == "eq-1"
    assert event["description"] == "Status changed"


@pytest.mark.asyncio
async def test_list_events_with_non_admin_returns_403(api_client) -> None:
    """GET /admin/events with regular user auth should return 403."""

    headers = await _get_auth_headers(api_client, username="regularuser")
    response = await api_client.get("/api/v1/admin/events", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_events_without_auth_returns_401(api_client) -> None:
    """GET /admin/events without auth should return 401."""

    response = await api_client.get("/api/v1/admin/events")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_clients_accepts_pagination_params(api_client) -> None:
    """GET /admin/clients should accept limit and offset query params."""

    headers = await _get_admin_headers(api_client)
    response = await api_client.get(
        "/api/v1/admin/clients?limit=5&offset=0", headers=headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_events_accepts_pagination_params(api_client) -> None:
    """GET /admin/events should accept limit and offset query params."""

    headers = await _get_admin_headers(api_client)
    response = await api_client.get(
        "/api/v1/admin/events?limit=5&offset=0", headers=headers
    )

    assert response.status_code == 200
