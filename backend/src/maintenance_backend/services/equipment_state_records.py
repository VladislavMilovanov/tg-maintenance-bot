"""State-record service contract and baseline implementation."""

from dataclasses import dataclass
from typing import Protocol

from maintenance_backend.repositories import StateRecordRepository
from maintenance_backend.schemas.equipment_state_records import (
    EquipmentStateRecordCreateRequest,
    EquipmentStateRecordResponse,
)


class StateRecordService(Protocol):
    """Equipment state record service contract."""

    async def create_record(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse: ...


@dataclass(slots=True)
class DefaultStateRecordService:
    """State record service backed by equipment and record repositories."""

    state_record_repository: StateRecordRepository

    async def create_record(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse:
        return await self.state_record_repository.create_or_get(request)
