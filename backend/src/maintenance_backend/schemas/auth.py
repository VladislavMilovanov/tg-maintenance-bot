"""Auth request/response schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    telegram_username: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    actor_id: str
    display_name: str | None = None
    role: str


class MeResponse(BaseModel):
    actor_id: str
    external_id: str
    display_name: str | None = None
    role: str
    is_active: bool
