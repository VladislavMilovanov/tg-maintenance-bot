"""Runtime SQLAlchemy database lifecycle helpers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from maintenance_backend.db_urls import to_sqlalchemy_async_url


class DatabaseGateway(Protocol):
    """Minimal database contract required by the backend runtime."""

    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def ping(self) -> None: ...


class PostgresDatabase:
    """Async SQLAlchemy database wrapper for backend runtime."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Return the configured async engine."""

        if self._engine is None:
            msg = "Database engine is not initialized."
            raise RuntimeError(msg)
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the configured async session factory."""

        if self._session_factory is None:
            msg = "Database session factory is not initialized."
            raise RuntimeError(msg)
        return self._session_factory

    async def connect(self) -> None:
        """Create async engine and session factory lazily."""

        if self._engine is not None:
            return

        self._engine = create_async_engine(
            to_sqlalchemy_async_url(self._database_url),
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        """Dispose engine if opened."""

        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield an async SQLAlchemy session."""

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def ping(self) -> None:
        """Validate database availability."""

        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
