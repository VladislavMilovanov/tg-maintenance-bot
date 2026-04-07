"""Schemas for dashboard endpoints: plant overview and feeds."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from maintenance_backend.schemas.common import Channel, EquipmentStatus


class StatusSummary(BaseModel):
    """Aggregated equipment status counts."""

    model_config = ConfigDict(from_attributes=True)

    normal: int
    warning: int
    critical: int
    unknown: int


class DailyStatusEntry(BaseModel):
    """Per-day status count breakdown."""

    model_config = ConfigDict(from_attributes=True)

    date: str
    normal: int
    warning: int
    critical: int
    unknown: int


class TrendInfo(BaseModel):
    """Week-over-week trend for status counts."""

    model_config = ConfigDict(from_attributes=True)

    critical_delta: int  # positive = more critical this week
    warning_delta: int
    direction: str  # "improved" | "worsened" | "stable"


class WorstPerformerEntry(BaseModel):
    """Equipment entry in worst performers list."""

    model_config = ConfigDict(from_attributes=True)

    equipment_id: str
    name: str
    current_status: EquipmentStatus
    location_name: str
    last_changed_at: datetime | None
    duration_in_status_hours: int | None = None
    last_comment: str | None = None


class PlantOverviewResponse(BaseModel):
    """Response for GET /dashboard/plant."""

    model_config = ConfigDict(from_attributes=True)

    plant_status: EquipmentStatus
    status_summary: StatusSummary
    daily_history: list[DailyStatusEntry]
    worst_performers: list[WorstPerformerEntry]
    trend: TrendInfo | None = None


class StateChangeEntry(BaseModel):
    """Single item in the state change feed."""

    model_config = ConfigDict(from_attributes=True)

    equipment_id: str
    equipment_name: str
    old_status: EquipmentStatus | None
    new_status: EquipmentStatus
    changed_at: datetime


class StateFeedResponse(BaseModel):
    """Response for GET /dashboard/state-feed."""

    model_config = ConfigDict(from_attributes=True)

    items: list[StateChangeEntry]
    total: int


class ActionFeedEntry(BaseModel):
    """Single item in the action feed."""

    model_config = ConfigDict(from_attributes=True)

    record_id: str
    equipment_id: str
    equipment_name: str
    status: EquipmentStatus
    comment: str | None
    author_name: str | None
    observed_at: datetime
    channel: Channel


class ActionFeedResponse(BaseModel):
    """Response for GET /dashboard/action-feed."""

    model_config = ConfigDict(from_attributes=True)

    items: list[ActionFeedEntry]
    total: int
