"""Equipment API routes — list, detail, and state history."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from maintenance_backend.dependencies import get_current_user, get_read_repository
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.schemas.equipment_read import (
    EquipmentDetailResponse,
    EquipmentHistoryResponse,
    EquipmentListResponse,
)

equipment_router = APIRouter(prefix="/equipment", tags=["equipment"])


@equipment_router.get("", response_model=EquipmentListResponse)
async def list_equipment(
    location_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> EquipmentListResponse:
    """Return paginated list of equipment with optional filters."""

    data = await repo.list_equipment(
        location_id=location_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return EquipmentListResponse(**data)


@equipment_router.get("/{equipment_id}", response_model=EquipmentDetailResponse)
async def get_equipment_detail(
    equipment_id: str,
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> EquipmentDetailResponse:
    """Return full detail for a single piece of equipment."""

    data = await repo.get_equipment_detail(equipment_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )
    return EquipmentDetailResponse(**data)


@equipment_router.get(
    "/{equipment_id}/history", response_model=EquipmentHistoryResponse
)
async def get_equipment_history(
    equipment_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> EquipmentHistoryResponse:
    """Return paginated state-record history for a piece of equipment."""

    data = await repo.get_equipment_history(
        equipment_id=equipment_id,
        limit=limit,
        offset=offset,
    )
    return EquipmentHistoryResponse(**data)
