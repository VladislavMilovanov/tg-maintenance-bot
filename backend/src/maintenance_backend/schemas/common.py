"""Shared schema primitives."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Channel(StrEnum):
    """Client channel that calls backend API."""

    TELEGRAM = "telegram"
    WEB = "web"


class UserRole(StrEnum):
    """Minimal caller role context."""

    USER = "user"
    ADMIN = "admin"
    OPERATOR = "operator"
    ENGINEER = "engineer"


class EquipmentStatus(StrEnum):
    """MVP equipment status enum."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ClientUser(BaseModel):
    """Client user descriptor."""

    model_config = ConfigDict(extra="forbid")

    external_id: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)
    role: UserRole | None = None


class StateRecordAuthor(BaseModel):
    """Author of a manual state record."""

    model_config = ConfigDict(extra="forbid")

    external_id: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)
    role: UserRole | None = None
