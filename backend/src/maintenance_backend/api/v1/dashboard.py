"""Dashboard API routes — plant overview and activity feeds."""

from fastapi import APIRouter, Depends, Query

from maintenance_backend.dependencies import get_current_user, get_read_repository
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.schemas.dashboard import (
    ActionFeedResponse,
    PlantOverviewResponse,
    StateFeedResponse,
)

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get("/plant", response_model=PlantOverviewResponse)
async def get_plant_overview(
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> PlantOverviewResponse:
    """Return aggregated plant status, daily history, and worst performers."""

    data = await repo.get_plant_overview()
    return PlantOverviewResponse(**data)


@dashboard_router.get("/state-feed", response_model=StateFeedResponse)
async def get_state_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> StateFeedResponse:
    """Return paginated equipment state-change feed."""

    data = await repo.get_state_feed(limit=limit, offset=offset)
    return StateFeedResponse(**data)


@dashboard_router.get("/action-feed", response_model=ActionFeedResponse)
async def get_action_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> ActionFeedResponse:
    """Return paginated state-record (action) feed."""

    data = await repo.get_action_feed(limit=limit, offset=offset)
    return ActionFeedResponse(**data)
