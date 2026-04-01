"""Equipment state record API endpoints."""

from fastapi import APIRouter, Depends, status

from maintenance_backend.dependencies import get_state_record_service
from maintenance_backend.schemas.equipment_state_records import (
    EquipmentStateRecordCreateRequest,
    EquipmentStateRecordResponse,
)
from maintenance_backend.services.equipment_state_records import StateRecordService

router = APIRouter(prefix="/equipment-state-records", tags=["equipment-state-records"])


@router.post(
    "", response_model=EquipmentStateRecordResponse, status_code=status.HTTP_201_CREATED
)
async def create_equipment_state_record(
    request: EquipmentStateRecordCreateRequest,
    state_record_service: StateRecordService = Depends(get_state_record_service),
) -> EquipmentStateRecordResponse:
    """Create a manual equipment state record."""

    return await state_record_service.create_record(request)
