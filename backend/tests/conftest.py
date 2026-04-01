"""Shared fixtures for backend API tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from maintenance_backend.app import create_app
from maintenance_backend.config import Settings
from maintenance_backend.exceptions import EquipmentNotFound, IdempotencyConflict
from maintenance_backend.gateways import AssistantGatewayError
from maintenance_backend.schemas.assistant import AssistantMessageRequest
from maintenance_backend.schemas.equipment_state_records import (
    EquipmentStateRecordCreateRequest,
    EquipmentStateRecordResponse,
)


@pytest.fixture
def settings() -> Settings:
    """Provide deterministic test settings."""

    return Settings(
        BACKEND_APP_ENV="test",
        BACKEND_HOST="127.0.0.1",
        BACKEND_PORT=8001,
        BACKEND_LOG_LEVEL="INFO",
        BACKEND_DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
    )


@pytest.fixture
def components():
    """Create fake runtime components for deterministic API tests."""

    equipment_ids = {"eq-1", "eq-42"}
    database = FakeDatabase()
    equipment_repository = FakeEquipmentRepository(equipment_ids=equipment_ids)
    state_record_repository = FakeStateRecordRepository(equipment_ids=equipment_ids)
    assistant_gateway = FakeAssistantGateway()
    return {
        "database": database,
        "equipment_repository": equipment_repository,
        "state_record_repository": state_record_repository,
        "assistant_gateway": assistant_gateway,
    }


@pytest.fixture
def app(settings: Settings, components):
    """Create a fresh application for each test."""

    return create_app(settings, components=components)


@pytest_asyncio.fixture
async def api_client(app):
    """Create async HTTP client bound to the ASGI app."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@dataclass(slots=True)
class FakeDatabase:
    """Lifecycle-compatible fake database for tests."""

    should_ping_fail: bool = False
    connected: bool = False

    async def connect(self) -> None:
        self.connected = True

    async def ensure_schema(self) -> None:
        return None

    async def seed_equipment(self, _: list[str]) -> None:
        return None

    async def close(self) -> None:
        self.connected = False

    async def ping(self) -> None:
        if self.should_ping_fail:
            raise RuntimeError("database unavailable")


@dataclass(slots=True)
class FakeEquipmentRepository:
    """In-memory equipment reference repository."""

    equipment_ids: set[str]

    async def exists(self, equipment_id: str) -> bool:
        return equipment_id in self.equipment_ids


@dataclass(slots=True)
class FakeStateRecordRepository:
    """In-memory state-record repository with idempotency behavior."""

    equipment_ids: set[str]
    records_by_key: dict[str, tuple[str, EquipmentStateRecordResponse]] = field(
        default_factory=dict
    )

    async def create_or_get(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse:
        payload_hash = self._build_payload_hash(request)
        if request.idempotency_key:
            existing = self.records_by_key.get(request.idempotency_key)
            if existing is not None:
                existing_hash, response = existing
                if existing_hash != payload_hash:
                    raise IdempotencyConflict()
                return response

        if request.equipment_id not in self.equipment_ids:
            raise EquipmentNotFound()

        response = EquipmentStateRecordResponse.model_validate(
            {
                "record_id": f"state-record-{len(self.records_by_key) + 1}",
                "equipment_id": request.equipment_id,
                "status": request.status,
                "comment": request.comment,
                "observed_at": request.observed_at,
                "created_at": datetime.now(tz=UTC),
                "channel": request.channel,
                "author": request.author,
            }
        )
        if request.idempotency_key:
            self.records_by_key[request.idempotency_key] = (payload_hash, response)
        return response

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> EquipmentStateRecordResponse | None:
        existing = self.records_by_key.get(idempotency_key)
        if existing is None:
            return None
        _, response = existing
        return response

    def _build_payload_hash(self, request: EquipmentStateRecordCreateRequest) -> str:
        payload = request.model_dump(mode="json", exclude={"idempotency_key"})
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class FakeAssistantGateway:
    """Test double for assistant gateway behavior."""

    mode: str = "success"

    async def generate_answer(
        self,
        request: AssistantMessageRequest,
        *,
        conversation_id: str,
    ) -> str:
        if self.mode in {"fail", "fail_hard"}:
            raise AssistantGatewayError("gateway unavailable")
        return f"gateway:{conversation_id}:{request.message.text}"

    async def close(self) -> None:
        return None
