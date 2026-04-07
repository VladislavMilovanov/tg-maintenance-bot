"""Locations API routes — hierarchical location tree."""

from fastapi import APIRouter, Depends

from maintenance_backend.dependencies import get_current_user, get_read_repository
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.schemas.locations import LocationTreeResponse

locations_router = APIRouter(prefix="/locations", tags=["locations"])


@locations_router.get("/tree", response_model=LocationTreeResponse)
async def get_location_tree(
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> LocationTreeResponse:
    """Return the full location hierarchy tree."""

    locations = await repo.get_location_tree()
    return LocationTreeResponse(locations=locations)
