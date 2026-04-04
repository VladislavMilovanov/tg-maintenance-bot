"""Integration fixtures for PostgreSQL-backed backend tests."""

from __future__ import annotations

import os

from alembic import command
from alembic.config import Config
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from maintenance_backend.app import create_app
from maintenance_backend.config import Settings
from maintenance_backend.db_urls import to_sqlalchemy_async_url
from maintenance_backend.gateways import AssistantGatewayError
from maintenance_backend.schemas.assistant import AssistantMessageRequest


TEST_DATABASE_URL = os.getenv(
    "BACKEND_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:55433/tg_maintenance",
)


class FakeAssistantGateway:
    """Deterministic gateway for integration tests."""

    async def generate_answer(
        self,
        request: AssistantMessageRequest,
        *,
        conversation_id: str,
    ) -> str:
        if request.message.text == "fail":
            raise AssistantGatewayError("gateway unavailable")
        return f"gateway:{conversation_id}:{request.message.text}"

    async def close(self) -> None:
        return None


def _run_migrations(database_url: str) -> None:
    os.environ["BACKEND_DATABASE_URL"] = database_url
    config = Config("alembic.ini")
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def integration_database_url() -> str:
    """Provide the integration database DSN."""

    return TEST_DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def migrated_database(integration_database_url: str) -> None:
    """Ensure the integration database is migrated before tests run."""

    _run_migrations(integration_database_url)


@pytest.fixture
def settings(integration_database_url: str) -> Settings:
    """Provide integration settings with a real PostgreSQL database."""

    return Settings(
        BACKEND_APP_ENV="test",
        BACKEND_HOST="127.0.0.1",
        BACKEND_PORT=8001,
        BACKEND_LOG_LEVEL="INFO",
        BACKEND_DATABASE_URL=integration_database_url,
    )


@pytest_asyncio.fixture
async def prepared_database(settings: Settings):
    """Reset the relevant tables and seed reference rows for each test."""

    engine = create_async_engine(to_sqlalchemy_async_url(settings.database_url))
    truncate_statements = (
        "TRUNCATE TABLE equipment_state_records RESTART IDENTITY CASCADE",
        "TRUNCATE TABLE equipment RESTART IDENTITY CASCADE",
        "TRUNCATE TABLE system_actors RESTART IDENTITY CASCADE",
        "TRUNCATE TABLE locations RESTART IDENTITY CASCADE",
    )
    seed_statements = (
        """
        INSERT INTO locations (location_id, name, location_type, display_order)
        VALUES ('loc-test', 'Test Location', 'site', 1)
        """,
        """
        INSERT INTO equipment (equipment_id, name, location_id, current_status)
        VALUES
            ('eq-1', 'Equipment 1', 'loc-test', 'normal'),
            ('eq-42', 'Equipment 42', 'loc-test', 'warning')
        """,
    )
    async with engine.begin() as connection:
        for statement in truncate_statements:
            await connection.execute(text(statement))
        for statement in seed_statements:
            await connection.execute(text(statement))
    await engine.dispose()
    yield


@pytest.fixture
def app(settings: Settings, prepared_database):
    """Create application wired to the real database and fake assistant gateway."""

    return create_app(
        settings, components={"assistant_gateway": FakeAssistantGateway()}
    )


@pytest_asyncio.fixture
async def api_client(app):
    """Create async HTTP client bound to the ASGI app."""

    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client
