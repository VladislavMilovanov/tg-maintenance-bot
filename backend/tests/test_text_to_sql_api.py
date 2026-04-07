"""Tests for the Text-to-SQL API endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from maintenance_backend.app import create_app
from maintenance_backend.config import Settings
from maintenance_backend.schemas.text_to_sql import TextToSqlResponse
from maintenance_backend.services.text_to_sql import (
    TextToSqlGatewayError,
    validate_sql,
)


# ---------------------------------------------------------------------------
# Fake gateway for deterministic tests
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class FakeTextToSqlGateway:
    """Test double: returns pre-configured SQL and summary."""

    sql_to_return: str = "SELECT COUNT(*) AS count FROM equipment WHERE current_status = 'critical'"
    summary_to_return: str = "В базе данных 5 единиц оборудования в статусе critical."
    fail_sql: bool = False
    fail_summary: bool = False

    async def generate_sql(self, question: str) -> str:
        if self.fail_sql:
            raise TextToSqlGatewayError("SQL generation failed")
        return self.sql_to_return

    async def summarize_results(
        self,
        question: str,
        sql_query: str,
        columns: list[str],
        rows: list[list[Any]],
    ) -> str:
        if self.fail_summary:
            raise TextToSqlGatewayError("Summarization failed")
        return self.summary_to_return

    async def close(self) -> None:
        pass


@dataclass(slots=True)
class FakeTextToSqlService:
    """Fully controlled fake service for endpoint-level tests."""

    response: TextToSqlResponse = field(
        default_factory=lambda: TextToSqlResponse(
            answer="Ответ на вопрос",
            sql_query="SELECT 1",
            row_count=1,
            columns=["count"],
            rows=[[1]],
        )
    )

    async def answer_question(
        self, question: str, user_role: str = "user"
    ) -> TextToSqlResponse:
        return self.response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def settings() -> Settings:
    return Settings(
        BACKEND_APP_ENV="test",
        BACKEND_HOST="127.0.0.1",
        BACKEND_PORT=8001,
        BACKEND_LOG_LEVEL="INFO",
        BACKEND_DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
    )


@pytest.fixture
def fake_text_to_sql_service():
    return FakeTextToSqlService()


@pytest.fixture
def components(fake_text_to_sql_service):
    """Minimal component overrides for text-to-sql tests."""

    from conftest import (
        FakeAuthService,
        FakeDatabase,
        FakeEquipmentRepository,
        FakeReadRepository,
        FakeStateRecordRepository,
    )

    equipment_ids = {"eq-1"}
    return {
        "database": FakeDatabase(),
        "equipment_repository": FakeEquipmentRepository(equipment_ids=equipment_ids),
        "state_record_repository": FakeStateRecordRepository(equipment_ids=equipment_ids),
        "auth_service": FakeAuthService(),
        "read_repository": FakeReadRepository(),
        "text_to_sql_service": fake_text_to_sql_service,
    }


@pytest.fixture
def app(settings, components):
    return create_app(settings, components=components)


@pytest_asyncio.fixture
async def api_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def auth_token(api_client):
    """Obtain a valid bearer token via login."""
    resp = await api_client.post(
        "/api/v1/auth/login",
        json={"telegram_username": "testuser"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def _query(
    client: AsyncClient,
    token: str,
    question: str,
) -> dict:
    resp = await client.post(
        "/api/v1/query/text-to-sql",
        json={"question": question},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_count_critical_equipment(
    api_client: AsyncClient,
    auth_token: str,
    fake_text_to_sql_service: FakeTextToSqlService,
):
    """Scenario 1: 'How many equipment units are in critical status?' -> returns count."""
    fake_text_to_sql_service.response = TextToSqlResponse(
        answer="В базе данных 5 единиц оборудования в статусе critical.",
        sql_query="SELECT COUNT(*) AS count FROM equipment WHERE current_status = 'critical'",
        row_count=1,
        columns=["count"],
        rows=[[5]],
    )

    resp = await _query(
        api_client,
        auth_token,
        "Сколько единиц оборудования в статусе critical?",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 1
    assert data["columns"] == ["count"]
    assert data["rows"] == [[5]]
    assert "5" in data["answer"]
    assert data["sql_query"] is not None
    assert data["error"] is None


@pytest.mark.asyncio
async def test_top3_problematic_equipment(
    api_client: AsyncClient,
    auth_token: str,
    fake_text_to_sql_service: FakeTextToSqlService,
):
    """Scenario 2: Top-3 problematic equipment over last 7 days."""
    fake_text_to_sql_service.response = TextToSqlResponse(
        answer="Топ-3 проблемного оборудования: Turbine 1, Pump 2, Compressor 3.",
        sql_query=(
            "SELECT e.name, COUNT(*) AS issue_count "
            "FROM equipment_state_records r "
            "JOIN equipment e ON r.equipment_id = e.equipment_id "
            "WHERE r.status IN ('critical','warning') "
            "AND r.observed_at > NOW() - INTERVAL '7 days' "
            "GROUP BY e.name ORDER BY issue_count DESC LIMIT 3"
        ),
        row_count=3,
        columns=["name", "issue_count"],
        rows=[["Turbine 1", 10], ["Pump 2", 7], ["Compressor 3", 5]],
    )

    resp = await _query(
        api_client,
        auth_token,
        "Покажи топ-3 проблемного оборудования за последние 7 дней",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 3
    assert "name" in data["columns"]
    assert len(data["rows"]) == 3
    assert data["error"] is None


@pytest.mark.asyncio
async def test_percentage_normal_equipment(
    api_client: AsyncClient,
    auth_token: str,
    fake_text_to_sql_service: FakeTextToSqlService,
):
    """Scenario 3: 'What percentage of equipment is in normal condition?'"""
    fake_text_to_sql_service.response = TextToSqlResponse(
        answer="60% оборудования находится в нормальном состоянии.",
        sql_query=(
            "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE current_status = 'normal') "
            "/ COUNT(*), 1) AS pct_normal FROM equipment"
        ),
        row_count=1,
        columns=["pct_normal"],
        rows=[[60.0]],
    )

    resp = await _query(
        api_client,
        auth_token,
        "Какой процент оборудования в нормальном состоянии?",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 1
    assert "pct_normal" in data["columns"]
    assert data["error"] is None


@pytest.mark.asyncio
async def test_locations_with_equipment_count(
    api_client: AsyncClient,
    auth_token: str,
    fake_text_to_sql_service: FakeTextToSqlService,
):
    """Scenario 4: Show all locations and count of equipment at each."""
    fake_text_to_sql_service.response = TextToSqlResponse(
        answer="Zone A: 3 единицы, Zone B: 2 единицы, Zone C: 1 единица.",
        sql_query=(
            "SELECT l.name AS location_name, COUNT(e.equipment_id) AS equipment_count "
            "FROM locations l "
            "LEFT JOIN equipment e ON e.location_id = l.location_id "
            "GROUP BY l.name ORDER BY equipment_count DESC LIMIT 100"
        ),
        row_count=3,
        columns=["location_name", "equipment_count"],
        rows=[["Zone A", 3], ["Zone B", 2], ["Zone C", 1]],
    )

    resp = await _query(
        api_client,
        auth_token,
        "Покажи все площадки и количество оборудования на каждой",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 3
    assert "location_name" in data["columns"]
    assert "equipment_count" in data["columns"]
    assert data["error"] is None


@pytest.mark.asyncio
async def test_mutation_query_rejected(
    api_client: AsyncClient,
    auth_token: str,
    fake_text_to_sql_service: FakeTextToSqlService,
):
    """Scenario 5: 'DELETE FROM equipment' — should be REJECTED by safety check."""
    fake_text_to_sql_service.response = TextToSqlResponse(
        answer="Запрос отклонён по соображениям безопасности.",
        sql_query="DELETE FROM equipment",
        error="Only SELECT statements are allowed. Got: 'DELETE'",
    )

    resp = await _query(
        api_client,
        auth_token,
        "DELETE FROM equipment",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is not None
    assert data["row_count"] == 0


# ---------------------------------------------------------------------------
# Unit tests for validate_sql (no HTTP, no DB)
# ---------------------------------------------------------------------------


def test_validate_sql_accepts_select():
    sql = "SELECT COUNT(*) FROM equipment WHERE current_status = 'critical'"
    result = validate_sql(sql)
    assert result == sql


def test_validate_sql_strips_trailing_semicolon():
    sql = "SELECT 1;"
    result = validate_sql(sql)
    assert result == "SELECT 1"


def test_validate_sql_rejects_delete():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("DELETE FROM equipment")


def test_validate_sql_rejects_insert():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("INSERT INTO equipment VALUES ('x','y','z')")


def test_validate_sql_rejects_mutation_inside_select():
    with pytest.raises(ValueError, match="Mutation keyword"):
        validate_sql("SELECT * FROM equipment; DROP TABLE equipment")


def test_validate_sql_rejects_update():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("UPDATE equipment SET current_status = 'critical'")


def test_validate_sql_rejects_drop():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("DROP TABLE equipment")


# ---------------------------------------------------------------------------
# Auth guard tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_requires_auth(api_client: AsyncClient):
    """Endpoint must reject unauthenticated requests."""
    resp = await api_client.post(
        "/api/v1/query/text-to-sql",
        json={"question": "How many equipment?"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_rejected(api_client: AsyncClient):
    """Endpoint must reject invalid bearer tokens."""
    resp = await api_client.post(
        "/api/v1/query/text-to-sql",
        json={"question": "How many equipment?"},
        headers={"Authorization": "Bearer invalid-token-xyz"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_empty_question_rejected(
    api_client: AsyncClient,
    auth_token: str,
):
    """Empty question must fail validation."""
    resp = await api_client.post(
        "/api/v1/query/text-to-sql",
        json={"question": ""},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code == 422
