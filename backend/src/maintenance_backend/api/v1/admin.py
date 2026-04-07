"""Admin API routes — dashboard KPIs, client list, and event feed."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from maintenance_backend.dependencies import get_current_user, get_read_repository
from maintenance_backend.schemas.admin import (
    AdminClientsResponse,
    AdminDashboardResponse,
    AdminEventsResponse,
)
from maintenance_backend.schemas.auth import MeResponse

admin_router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: MeResponse) -> MeResponse:
    """Raise 403 if the caller is not an admin."""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@admin_router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> AdminDashboardResponse:
    """Return admin KPIs, activity chart, and progress matrix."""

    _require_admin(current_user)
    data = await repo.get_admin_dashboard()
    return AdminDashboardResponse(**data)


@admin_router.get("/clients", response_model=AdminClientsResponse)
async def list_clients(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> AdminClientsResponse:
    """Return paginated list of system actors (clients)."""

    _require_admin(current_user)
    data = await repo.list_clients(limit=limit, offset=offset)
    return AdminClientsResponse(**data)


@admin_router.get("/events", response_model=AdminEventsResponse)
async def list_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> AdminEventsResponse:
    """Return paginated unified event feed (state changes + actions)."""

    _require_admin(current_user)
    data = await repo.list_events(limit=limit, offset=offset)
    return AdminEventsResponse(**data)
