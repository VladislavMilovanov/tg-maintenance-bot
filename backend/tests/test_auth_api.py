"""Tests for auth API endpoints: login and /me."""

import pytest


async def _get_auth_headers(api_client, username: str = "testuser") -> dict[str, str]:
    resp = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": username}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_login_with_valid_username_returns_200(api_client) -> None:
    """Login with a valid username should return 200 with a bearer token."""

    response = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": "testuser"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"] == "test-token-testuser"
    assert payload["token_type"] == "bearer"
    assert payload["actor_id"] == "actor-testuser"
    assert payload["display_name"] == "testuser"
    assert payload["role"] == "user"


@pytest.mark.asyncio
async def test_login_with_empty_username_returns_422(api_client) -> None:
    """Login with an empty username should return 422 validation error."""

    response = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": ""}
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"


@pytest.mark.asyncio
async def test_login_without_username_field_returns_422(api_client) -> None:
    """Login without the required telegram_username field should return 422."""

    response = await api_client.post("/api/v1/auth/login", json={})

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"


@pytest.mark.asyncio
async def test_me_with_valid_token_returns_200(api_client) -> None:
    """GET /me with a valid bearer token should return the current actor info."""

    headers = await _get_auth_headers(api_client, username="alice")
    response = await api_client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["actor_id"] == "actor-alice"
    assert payload["external_id"] == "web:alice"
    assert payload["display_name"] == "alice"
    assert payload["role"] == "user"
    assert payload["is_active"] is True


@pytest.mark.asyncio
async def test_me_without_token_returns_401(api_client) -> None:
    """GET /me without any Authorization header should return 401."""

    response = await api_client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token_returns_401(api_client) -> None:
    """GET /me with an invalid bearer token should return 401."""

    response = await api_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token-xyz"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_returns_admin_role(api_client) -> None:
    """Login as 'admin' username should return admin role."""

    response = await api_client.post(
        "/api/v1/auth/login", json={"telegram_username": "admin"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "admin"
    assert payload["actor_id"] == "actor-admin"
