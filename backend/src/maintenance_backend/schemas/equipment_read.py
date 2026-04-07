"""Schemas for equipment read endpoints: list, detail, and history."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import (
    Channel,
    EquipmentStatus,
    StateRecordAuthor,
)


class LocationBrief(BaseModel):
    """Brief location descriptor embedded in equipment responses."""

    model_config = ConfigDict(from_attributes=True)

    location_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class ActorBrief(BaseModel):
    """Brief actor/owner descriptor embedded in equipment responses."""

    model_config = ConfigDict(from_attributes=True)

    actor_id: str = Field(min_length=1)
    display_name: str | None


class SensorGroupBrief(BaseModel):
    """Brief sensor group descriptor in equipment detail top_nodes."""

    model_config = ConfigDict(from_attributes=True)

    sensor_group_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: EquipmentStatus
    group_type: str = Field(min_length=1)


class EquipmentListItem(BaseModel):
    """Single item in the paginated equipment list."""

    model_config = ConfigDict(from_attributes=True)

    equipment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    equipment_code: str | None
    current_status: EquipmentStatus
    location: LocationBrief
    owner: ActorBrief | None


class EquipmentListResponse(BaseModel):
    """Response for GET /equipment."""

    model_config = ConfigDict(from_attributes=True)

    items: list[EquipmentListItem]
    total: int


class EquipmentDetailResponse(BaseModel):
    """Response for GET /equipment/{equipment_id}."""

    model_config = ConfigDict(from_attributes=True)

    equipment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    equipment_code: str | None
    current_status: EquipmentStatus
    location: LocationBrief
    owner: ActorBrief | None
    maintenance_progress: float | None = Field(default=None, ge=0, le=1)
    top_nodes: list[SensorGroupBrief]
    sensor_groups_count: int
    last_state_change: datetime | None
    duration_in_status_hours: int | None = None


class EquipmentHistoryEntry(BaseModel):
    """Single history entry in equipment state history."""

    model_config = ConfigDict(from_attributes=True)

    record_id: str = Field(min_length=1)
    status: EquipmentStatus
    comment: str | None
    observed_at: datetime
    created_at: datetime
    channel: Channel
    author: StateRecordAuthor


class EquipmentHistoryResponse(BaseModel):
    """Response for GET /equipment/{equipment_id}/history."""

    model_config = ConfigDict(from_attributes=True)

    items: list[EquipmentHistoryEntry]
    total: int
