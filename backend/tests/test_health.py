"""Smoke tests for backend service skeleton."""

import pytest


@pytest.mark.asyncio
async def test_healthcheck_returns_ok(api_client) -> None:
    """Health endpoint should confirm backend liveness."""

    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_returns_ok(api_client) -> None:
    """Readiness endpoint should succeed when fake database pings successfully."""

    response = await api_client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_returns_503_when_database_is_unavailable(
    app, api_client
) -> None:
    """Readiness endpoint should fail when database ping fails."""

    app.state.database.should_ping_fail = True

    response = await api_client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "code": "service_unavailable",
        "message": "Service is not ready.",
        "details": None,
        "trace_id": None,
    }
