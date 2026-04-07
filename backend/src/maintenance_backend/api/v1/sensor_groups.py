"""Sensor group API routes — detail view."""

from fastapi import APIRouter, Depends, HTTPException, status

from maintenance_backend.dependencies import get_current_user, get_read_repository
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.schemas.sensor_groups import SensorGroupDetailResponse

sensor_groups_router = APIRouter(prefix="/sensor-groups", tags=["sensor-groups"])


@sensor_groups_router.get(
    "/{sensor_group_id}", response_model=SensorGroupDetailResponse
)
async def get_sensor_group_detail(
    sensor_group_id: str,
    current_user: MeResponse = Depends(get_current_user),
    repo=Depends(get_read_repository),
) -> SensorGroupDetailResponse:
    """Return full detail for a single sensor group including its sensors."""

    data = await repo.get_sensor_group_detail(sensor_group_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor group not found",
        )
    return SensorGroupDetailResponse(**data)
