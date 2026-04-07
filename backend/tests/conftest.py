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
from maintenance_backend.schemas.auth import LoginResponse, MeResponse
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
    auth_service = FakeAuthService()
    read_repository = FakeReadRepository()
    return {
        "database": database,
        "equipment_repository": equipment_repository,
        "state_record_repository": state_record_repository,
        "assistant_gateway": assistant_gateway,
        "auth_service": auth_service,
        "read_repository": read_repository,
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


class FakeAuthService:
    """In-memory auth for tests — no database required."""

    def __init__(self):
        self.token_store: dict[str, str] = {}
        self._actors: dict[str, dict] = {}

    async def login(self, telegram_username: str) -> LoginResponse:
        actor_id = f"actor-{telegram_username}"
        token = f"test-token-{telegram_username}"
        role = "admin" if telegram_username == "admin" else "user"
        self.token_store[token] = actor_id
        self._actors[actor_id] = {
            "actor_id": actor_id,
            "external_id": f"web:{telegram_username}",
            "display_name": telegram_username,
            "role": role,
            "is_active": True,
        }
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            actor_id=actor_id,
            display_name=telegram_username,
            role=role,
        )

    async def get_current_actor(self, token: str) -> MeResponse | None:
        actor_id = self.token_store.get(token)
        if not actor_id:
            return None
        actor = self._actors.get(actor_id)
        if not actor:
            return None
        return MeResponse(**actor)


class FakeReadRepository:
    """Returns hardcoded data for all read endpoints — no database required."""

    async def get_plant_overview(self):
        return {
            "plant_status": "warning",
            "status_summary": {"normal": 3, "warning": 1, "critical": 1, "unknown": 0},
            "daily_history": [
                {"date": "2026-04-01", "normal": 3, "warning": 1, "critical": 1, "unknown": 0}
            ],
            "worst_performers": [
                {
                    "equipment_id": "eq-1",
                    "name": "Turbine 1",
                    "current_status": "critical",
                    "location_name": "Zone A",
                    "last_changed_at": "2026-04-01T10:00:00Z",
                }
            ],
        }

    async def get_state_feed(self, limit=20, offset=0):
        return {
            "items": [
                {
                    "equipment_id": "eq-1",
                    "equipment_name": "Turbine 1",
                    "old_status": "normal",
                    "new_status": "warning",
                    "changed_at": "2026-04-01T10:00:00Z",
                }
            ],
            "total": 1,
        }

    async def get_action_feed(self, limit=20, offset=0):
        return {
            "items": [
                {
                    "record_id": "rec-1",
                    "equipment_id": "eq-1",
                    "equipment_name": "Turbine 1",
                    "status": "warning",
                    "comment": "Test",
                    "observed_at": "2026-04-01T10:00:00Z",
                    "author_name": "Admin",
                    "channel": "web",
                }
            ],
            "total": 1,
        }

    async def list_equipment(self, location_id=None, status=None, limit=20, offset=0):
        return {
            "items": [
                {
                    "equipment_id": "eq-1",
                    "name": "Turbine 1",
                    "equipment_code": "GT-001",
                    "current_status": "normal",
                    "location": {"location_id": "loc-1", "name": "Zone A"},
                    "owner": None,
                }
            ],
            "total": 1,
        }

    async def get_equipment_detail(self, equipment_id: str):
        if equipment_id == "nonexistent":
            return None
        return {
            "equipment_id": equipment_id,
            "name": "Turbine 1",
            "equipment_code": "GT-001",
            "current_status": "normal",
            "location": {"location_id": "loc-1", "name": "Zone A"},
            "owner": {"actor_id": "a-1", "display_name": "Engineer"},
            "maintenance_progress": 0.5,
            "top_nodes": [],
            "sensor_groups_count": 2,
            "last_state_change": None,
        }

    async def get_equipment_history(self, equipment_id: str, limit=20, offset=0):
        return {"items": [], "total": 0}

    async def get_sensor_group_detail(self, sensor_group_id: str):
        if sensor_group_id == "nonexistent":
            return None
        return {
            "sensor_group_id": sensor_group_id,
            "name": "Vibration",
            "group_type": "vibration",
            "status": "normal",
            "image_url": None,
            "equipment": {"equipment_id": "eq-1", "name": "Turbine 1"},
            "sensors": [
                {
                    "sensor_id": "s-1",
                    "name": "Sensor A",
                    "sensor_type": "vibration",
                    "last_observed_at": None,
                }
            ],
        }

    async def get_location_tree(self):
        return [
            {
                "location_id": "loc-1",
                "name": "Plant",
                "location_type": "plant",
                "status": "normal",
                "equipment_count": 5,
                "children": [],
            }
        ]

    async def get_admin_dashboard(self):
        return {
            "kpis": {
                "total_equipment": 5,
                "critical_count": 1,
                "warning_count": 1,
                "clients_count": 3,
            },
            "activity_chart": [{"date": "2026-04-01", "actions_count": 5}],
            "progress_matrix": [
                {
                    "location_name": "Zone A",
                    "total": 3,
                    "normal": 2,
                    "warning": 1,
                    "critical": 0,
                }
            ],
        }

    async def list_clients(self, limit=20, offset=0):
        return {
            "items": [
                {
                    "actor_id": "a-1",
                    "external_id": "web:admin",
                    "display_name": "Admin",
                    "role": "admin",
                    "equipment_count": 3,
                    "last_activity_at": None,
                }
            ],
            "total": 1,
        }

    async def list_events(self, limit=20, offset=0):
        return {
            "items": [
                {
                    "event_type": "state_change",
                    "equipment_id": "eq-1",
                    "equipment_name": "Turbine 1",
                    "actor_name": None,
                    "description": "Status changed",
                    "occurred_at": "2026-04-01T10:00:00Z",
                }
            ],
            "total": 1,
        }
