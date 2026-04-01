"""FastAPI application factory for the backend service."""

from contextlib import asynccontextmanager
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from maintenance_backend.api.health import router as health_router
from maintenance_backend.api.v1.router import api_v1_router
from maintenance_backend.conversations import InMemoryConversationStore
from maintenance_backend.config import Settings
from maintenance_backend.database import PostgresDatabase
from maintenance_backend.exceptions import BackendError
from maintenance_backend.gateways import OpenRouterAssistantGateway
from maintenance_backend.logging import build_request_log_message, configure_logging
from maintenance_backend.repositories import (
    PostgresEquipmentRepository,
    PostgresStateRecordRepository,
)
from maintenance_backend.schemas.errors import ErrorDetail, ErrorResponse
from maintenance_backend.services.assistant import DefaultAssistantService
from maintenance_backend.services.equipment_state_records import (
    DefaultStateRecordService,
)

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    components: dict[str, Any] | None = None,
) -> FastAPI:
    """Create and configure the backend ASGI application."""

    runtime_settings = settings or Settings()
    runtime_components = _build_components(runtime_settings, overrides=components or {})
    configure_logging(runtime_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(
            "Starting backend service",
            extra={
                "app_env": runtime_settings.app_env,
                "host": runtime_settings.host,
                "port": runtime_settings.port,
            },
        )
        database = app.state.database
        await database.connect()
        await database.ensure_schema()
        await database.seed_equipment(runtime_settings.seed_equipment_ids)
        try:
            yield
        finally:
            gateway = getattr(app.state, "assistant_gateway", None)
            if gateway is not None and hasattr(gateway, "close"):
                await gateway.close()
            await database.close()
            logger.info("Stopping backend service")

    app = FastAPI(
        title="TG Maintenance Backend",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = runtime_settings
    for key, value in runtime_components.items():
        setattr(app.state, key, value)

    @app.middleware("http")
    async def log_request_metrics(request: Request, call_next):
        request_body = await request.body()
        response = await call_next(request)
        response_size = _resolve_response_size(response)
        logger.info(
            build_request_log_message(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                request_body=request_body,
                response_size=response_size,
            )
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(item) for item in error["loc"] if item != "body"),
                issue=error["msg"],
            )
            for error in exc.errors()
        ]
        payload = ErrorResponse(
            code="validation_error",
            message="Request validation failed.",
            details=details,
            trace_id=None,
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @app.exception_handler(BackendError)
    async def handle_backend_error(_: Request, exc: BackendError) -> JSONResponse:
        payload = ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            trace_id=exc.trace_id,
        )
        return JSONResponse(
            status_code=exc.status_code, content=payload.model_dump(mode="json")
        )

    app.include_router(health_router)
    app.include_router(api_v1_router)
    return app


def _build_components(settings: Settings, overrides: dict[str, Any]) -> dict[str, Any]:
    database = overrides.get("database") or PostgresDatabase(settings.database_url)
    equipment_repository = overrides.get(
        "equipment_repository"
    ) or PostgresEquipmentRepository(database=database)
    state_record_repository = overrides.get(
        "state_record_repository"
    ) or PostgresStateRecordRepository(database=database)
    conversation_store = overrides.get(
        "conversation_store"
    ) or InMemoryConversationStore(ttl_seconds=settings.conversation_ttl_seconds)
    assistant_gateway = overrides.get(
        "assistant_gateway"
    ) or OpenRouterAssistantGateway(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.openrouter_model,
        timeout_seconds=settings.openrouter_timeout_seconds,
        system_prompt=settings.openrouter_system_prompt,
    )
    assistant_service = overrides.get("assistant_service") or DefaultAssistantService(
        gateway=assistant_gateway,
        equipment_repository=equipment_repository,
        conversation_store=conversation_store,
    )
    state_record_service = overrides.get(
        "state_record_service"
    ) or DefaultStateRecordService(
        state_record_repository=state_record_repository,
    )
    return {
        "database": database,
        "equipment_repository": equipment_repository,
        "state_record_repository": state_record_repository,
        "conversation_store": conversation_store,
        "assistant_gateway": assistant_gateway,
        "assistant_service": assistant_service,
        "state_record_service": state_record_service,
    }


def _resolve_response_size(response: JSONResponse) -> int:
    content_length = response.headers.get("content-length")
    if content_length is not None:
        try:
            return int(content_length)
        except ValueError:
            pass
    body = getattr(response, "body", b"")
    if isinstance(body, bytes):
        return len(body)
    return 0
