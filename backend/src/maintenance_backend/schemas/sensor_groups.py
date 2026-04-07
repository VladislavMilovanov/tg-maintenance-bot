"""Schemas for sensor group endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import EquipmentStatus


class EquipmentBrief(BaseModel):
    """Brief equipment descriptor embedded in sensor group responses."""

    model_config = ConfigDict(from_attributes=True)

    equipment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class SensorEntry(BaseModel):
    """Single sensor in a sensor group."""

    model_config = ConfigDict(from_attributes=True)

    sensor_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    sensor_type: str = Field(min_length=1)
    last_observed_at: datetime | None


class SensorGroupDetailResponse(BaseModel):
    """Response for GET /sensor-groups/{sensor_group_id}."""

    model_config = ConfigDict(from_attributes=True)

    sensor_group_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: EquipmentStatus
    group_type: str = Field(min_length=1)
    image_url: str | None
    equipment: EquipmentBrief
    sensors: list[SensorEntry]
