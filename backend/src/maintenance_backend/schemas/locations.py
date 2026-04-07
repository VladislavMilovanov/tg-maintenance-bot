"""Schemas for location hierarchy endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import EquipmentStatus


class LocationTreeNode(BaseModel):
    """A node in the hierarchical location tree."""

    model_config = ConfigDict(from_attributes=True)

    location_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    location_type: str = Field(min_length=1)
    status: EquipmentStatus
    equipment_count: int
    children: list[LocationTreeNode]


LocationTreeNode.model_rebuild()


class LocationTreeResponse(BaseModel):
    """Response for GET /locations/tree."""

    model_config = ConfigDict(from_attributes=True)

    locations: list[LocationTreeNode]
