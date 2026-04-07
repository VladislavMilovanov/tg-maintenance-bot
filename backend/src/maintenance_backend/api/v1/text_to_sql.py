"""Text-to-SQL API endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from maintenance_backend.dependencies import get_current_user, get_text_to_sql_service
from maintenance_backend.schemas.auth import MeResponse
from maintenance_backend.schemas.text_to_sql import TextToSqlRequest, TextToSqlResponse
from maintenance_backend.services.text_to_sql import TextToSqlService

text_to_sql_router = APIRouter(prefix="/query", tags=["query"])


@text_to_sql_router.post(
    "/text-to-sql",
    response_model=TextToSqlResponse,
    summary="Answer a natural language question about database data",
)
async def query_text_to_sql(
    request: TextToSqlRequest,
    current_user: MeResponse = Depends(get_current_user),
    service: TextToSqlService = Depends(get_text_to_sql_service),
) -> TextToSqlResponse:
    """Convert a natural language question to SQL, execute it, and return a summarized answer."""

    return await service.answer_question(
        question=request.question,
        user_role=current_user.role or "user",
    )
