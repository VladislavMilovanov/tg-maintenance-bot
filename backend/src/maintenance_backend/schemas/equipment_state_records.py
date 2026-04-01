"""Schemas for manual equipment state records."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import (
    Channel,
    EquipmentStatus,
    StateRecordAuthor,
)


class EquipmentStateRecordCreateRequest(BaseModel):
    """Request for manual equipment state recording."""

    model_config = ConfigDict(extra="forbid")

    equipment_id: str = Field(min_length=1)
    status: EquipmentStatus
    comment: str | None = Field(default=None, max_length=2000)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)
    observed_at: datetime
    channel: Channel
    author: StateRecordAuthor


class EquipmentStateRecordResponse(BaseModel):
    """Response for created equipment state record."""

    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    equipment_id: str = Field(min_length=1)
    status: EquipmentStatus
    comment: str | None = None
    observed_at: datetime
    created_at: datetime
    channel: Channel
    author: StateRecordAuthor
