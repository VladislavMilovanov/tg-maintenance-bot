"""Unified error payloads."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Structured field-level error detail."""

    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    issue: str = Field(min_length=1)


class ErrorResponse(BaseModel):
    """Unified API error shape."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: list[ErrorDetail] | None = None
    trace_id: str | None = Field(default=None, min_length=1)
