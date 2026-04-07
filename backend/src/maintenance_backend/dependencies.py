"""Dependency providers for backend routes."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from maintenance_backend.database import DatabaseGateway
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.services.assistant import AssistantService
from maintenance_backend.services.auth import AuthService
from maintenance_backend.services.equipment_state_records import StateRecordService
from maintenance_backend.services.text_to_sql import TextToSqlService

_bearer_scheme = HTTPBearer(auto_error=False)


def get_text_to_sql_service(request: Request) -> TextToSqlService:
    """Provide Text-to-SQL service from the application container."""

    return request.app.state.text_to_sql_service


def get_assistant_service(request: Request) -> AssistantService:
    """Provide assistant service implementation from the application container."""

    return request.app.state.assistant_service


def get_state_record_service(request: Request) -> StateRecordService:
    """Provide state-record service implementation from the application container."""

    return request.app.state.state_record_service


def get_database(request: Request) -> DatabaseGateway:
    """Provide application database adapter."""

    return request.app.state.database


def get_auth_service(request: Request) -> AuthService:
    """Provide auth service implementation from the application container."""

    return request.app.state.auth_service


def get_read_repository(request: Request):
    """Provide read-only repository from the application container."""

    return request.app.state.read_repository


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> MeResponse:
    """Resolve the current authenticated actor from the bearer token."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    auth_service: AuthService = request.app.state.auth_service
    user = await auth_service.get_current_actor(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user
