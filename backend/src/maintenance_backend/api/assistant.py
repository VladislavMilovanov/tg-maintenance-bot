"""Assistant scenario API endpoints."""

from fastapi import APIRouter, Depends

from maintenance_backend.dependencies import get_assistant_service
from maintenance_backend.schemas.assistant import (
    AssistantMessageRequest,
    AssistantMessageResponse,
)
from maintenance_backend.services.assistant import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/messages", response_model=AssistantMessageResponse)
async def create_assistant_message(
    request: AssistantMessageRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> AssistantMessageResponse:
    """Create assistant response for a client message."""

    return await assistant_service.create_response(request)
