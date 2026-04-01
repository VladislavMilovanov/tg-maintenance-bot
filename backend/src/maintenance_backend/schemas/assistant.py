"""Schemas for the assistant API scenario."""

from pydantic import BaseModel, ConfigDict, Field

from maintenance_backend.schemas.common import Channel, ClientUser


class AssistantMessagePayload(BaseModel):
    """Assistant message payload."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)


class EquipmentContext(BaseModel):
    """Optional equipment context supplied by client."""

    model_config = ConfigDict(extra="forbid")

    equipment_id: str | None = Field(default=None, min_length=1)
    sensor_ids: list[str] = Field(default_factory=list)
    sensor_group_ids: list[str] = Field(default_factory=list)


class AssistantMessageRequest(BaseModel):
    """Assistant scenario request."""

    model_config = ConfigDict(extra="forbid")

    channel: Channel
    user: ClientUser
    conversation_id: str | None = Field(default=None, min_length=1)
    message: AssistantMessagePayload
    equipment_context: EquipmentContext | None = None


class AssistantResponseMeta(BaseModel):
    """Metadata about assistant response generation."""

    model_config = ConfigDict(extra="forbid")

    fallback_used: bool
    trace_id: str | None = Field(default=None, min_length=1)


class ContextUsed(BaseModel):
    """Context effectively used by backend."""

    model_config = ConfigDict(extra="forbid")

    equipment_id: str | None = None
    sensor_ids: list[str] = Field(default_factory=list)
    sensor_group_ids: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class AssistantMessageResponse(BaseModel):
    """Assistant scenario response."""

    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    context_used: ContextUsed | None = None
    meta: AssistantResponseMeta
