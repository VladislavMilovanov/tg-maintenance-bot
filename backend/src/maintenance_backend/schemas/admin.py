"""Schemas for admin panel endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import UserRole


class AdminKpis(BaseModel):
    """Admin KPI metrics."""

    model_config = ConfigDict(from_attributes=True)

    total_equipment: int
    critical_count: int
    warning_count: int
    clients_count: int


class ActivityChartEntry(BaseModel):
    """Single day entry in the activity chart."""

    model_config = ConfigDict(from_attributes=True)

    date: str
    actions_count: int


class ProgressMatrixEntry(BaseModel):
    """Single location row in the progress matrix."""

    model_config = ConfigDict(from_attributes=True)

    location_name: str = Field(min_length=1)
    total: int
    normal: int
    warning: int
    critical: int


class AdminDashboardResponse(BaseModel):
    """Response for GET /admin/dashboard."""

    model_config = ConfigDict(from_attributes=True)

    kpis: AdminKpis
    activity_chart: list[ActivityChartEntry]
    progress_matrix: list[ProgressMatrixEntry]


class AdminClientEntry(BaseModel):
    """Single client entry in the admin clients list."""

    model_config = ConfigDict(from_attributes=True)

    actor_id: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    display_name: str | None
    role: UserRole | None
    equipment_count: int
    last_activity_at: datetime | None


class AdminClientsResponse(BaseModel):
    """Response for GET /admin/clients."""

    model_config = ConfigDict(from_attributes=True)

    items: list[AdminClientEntry]
    total: int


class AdminEventEntry(BaseModel):
    """Single event entry in the admin events feed."""

    model_config = ConfigDict(from_attributes=True)

    event_type: str = Field(min_length=1)
    equipment_id: str | None
    equipment_name: str | None
    actor_name: str | None
    description: str = Field(min_length=1)
    occurred_at: datetime


class AdminEventsResponse(BaseModel):
    """Response for GET /admin/events."""

    model_config = ConfigDict(from_attributes=True)

    items: list[AdminEventEntry]
    total: int
