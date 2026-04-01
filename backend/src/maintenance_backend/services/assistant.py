"""Assistant service contract and implementation."""

from dataclasses import dataclass
from typing import Protocol

from maintenance_backend.conversations import ConversationStore
from maintenance_backend.exceptions import (
    AssistantContextValidationError,
    AssistantUnavailable,
)
from maintenance_backend.gateways import AssistantGateway, AssistantGatewayError
from maintenance_backend.repositories import EquipmentRepository
from maintenance_backend.schemas.assistant import (
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantResponseMeta,
    ContextUsed,
)
from maintenance_backend.schemas.errors import ErrorDetail

FALLBACK_ANSWER = "Не удалось получить штатную интерпретацию. Попробуйте позже."


class AssistantService(Protocol):
    """Assistant interaction service contract."""

    async def create_response(
        self,
        request: AssistantMessageRequest,
    ) -> AssistantMessageResponse: ...


@dataclass(slots=True)
class DefaultAssistantService:
    """Assistant service with OpenRouter gateway and fallback behavior."""

    gateway: AssistantGateway
    equipment_repository: EquipmentRepository
    conversation_store: ConversationStore

    async def create_response(
        self,
        request: AssistantMessageRequest,
    ) -> AssistantMessageResponse:
        conversation_id = await self.conversation_store.resolve(request.conversation_id)
        context_used = await self._build_context_used(request)

        try:
            answer = await self.gateway.generate_answer(
                request, conversation_id=conversation_id
            )
            return AssistantMessageResponse(
                answer=answer,
                conversation_id=conversation_id,
                context_used=context_used,
                meta=AssistantResponseMeta(fallback_used=False, trace_id=None),
            )
        except AssistantGatewayError:
            try:
                fallback_answer = self._build_fallback_answer(request)
            except Exception as exc:
                raise AssistantUnavailable() from exc
            return AssistantMessageResponse(
                answer=fallback_answer,
                conversation_id=conversation_id,
                context_used=context_used,
                meta=AssistantResponseMeta(fallback_used=True, trace_id=None),
            )

    async def _build_context_used(
        self,
        request: AssistantMessageRequest,
    ) -> ContextUsed | None:
        if request.equipment_context is None:
            return None

        equipment_id = request.equipment_context.equipment_id
        if equipment_id is not None and not await self.equipment_repository.exists(
            equipment_id
        ):
            raise AssistantContextValidationError(
                details=[
                    ErrorDetail(
                        field="equipment_context.equipment_id",
                        issue="Equipment was not found.",
                    )
                ]
            )

        return ContextUsed(
            equipment_id=equipment_id,
            sensor_ids=request.equipment_context.sensor_ids,
            sensor_group_ids=request.equipment_context.sensor_group_ids,
            sources=["client_payload"],
        )

    def _build_fallback_answer(self, _: AssistantMessageRequest) -> str:
        return FALLBACK_ANSWER
