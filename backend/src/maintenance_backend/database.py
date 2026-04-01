"""Database lifecycle and schema helpers for PostgreSQL."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS equipment (
        equipment_id TEXT PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS equipment_state_records (
        record_id TEXT PRIMARY KEY,
        equipment_id TEXT NOT NULL REFERENCES equipment (equipment_id),
        status TEXT NOT NULL,
        comment TEXT,
        observed_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        channel TEXT NOT NULL,
        author_external_id TEXT NOT NULL,
        author_display_name TEXT,
        author_role TEXT,
        idempotency_key TEXT UNIQUE,
        payload_hash TEXT
    )
    """,
)


class PostgresDatabase:
    """Thin asyncpg-backed database wrapper."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: Any = None

    @property
    def pool(self) -> Any:
        """Return the underlying asyncpg pool after connection."""

        if self._pool is None:
            msg = "Database pool is not initialized."
            raise RuntimeError(msg)
        return self._pool

    async def connect(self) -> None:
        """Create asyncpg pool lazily."""

        if self._pool is not None:
            return

        import asyncpg

        self._pool = await asyncpg.create_pool(
            dsn=self._database_url, min_size=1, max_size=5
        )

    async def close(self) -> None:
        """Close pool if opened."""

        if self._pool is None:
            return
        await self._pool.close()
        self._pool = None

    async def ensure_schema(self) -> None:
        """Create minimal MVP schema required by task 05."""

        async with self.pool.acquire() as connection:
            for statement in SCHEMA_STATEMENTS:
                await connection.execute(statement)

    async def seed_equipment(self, equipment_ids: Sequence[str]) -> None:
        """Insert configured reference equipment rows if they do not exist."""

        normalized_ids = [
            equipment_id.strip()
            for equipment_id in equipment_ids
            if equipment_id.strip()
        ]
        if not normalized_ids:
            return

        async with self.pool.acquire() as connection:
            await connection.executemany(
                """
                INSERT INTO equipment (equipment_id, name)
                VALUES ($1, $2)
                ON CONFLICT (equipment_id) DO NOTHING
                """,
                [(equipment_id, equipment_id) for equipment_id in normalized_ids],
            )

    async def ping(self) -> None:
        """Validate database availability."""

        async with self.pool.acquire() as connection:
            await connection.execute("SELECT 1")
