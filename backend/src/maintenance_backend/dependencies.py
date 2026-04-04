"""Dependency providers for backend routes."""

from fastapi import Request

from maintenance_backend.database import DatabaseGateway
from maintenance_backend.services.assistant import AssistantService
from maintenance_backend.services.equipment_state_records import StateRecordService


def get_assistant_service(request: Request) -> AssistantService:
    """Provide assistant service implementation from the application container."""

    return request.app.state.assistant_service


def get_state_record_service(request: Request) -> StateRecordService:
    """Provide state-record service implementation from the application container."""

    return request.app.state.state_record_service


def get_database(request: Request) -> DatabaseGateway:
    """Provide application database adapter."""

    return request.app.state.database
