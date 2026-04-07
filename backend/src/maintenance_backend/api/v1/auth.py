"""Auth API routes — login and session introspection."""

from fastapi import APIRouter, Depends

from maintenance_backend.dependencies import get_auth_service, get_current_user
from maintenance_backend.schemas.auth import LoginRequest, LoginResponse, MeResponse
from maintenance_backend.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Exchange a Telegram username for a bearer token."""

    return await auth_service.login(body.telegram_username)


@auth_router.get("/me", response_model=MeResponse)
async def me(
    current_user: MeResponse = Depends(get_current_user),
) -> MeResponse:
    """Return the actor that owns the current bearer token."""

    return current_user
