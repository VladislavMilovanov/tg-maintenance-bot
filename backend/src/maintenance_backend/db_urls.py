"""Helpers for adapting DB URLs across sync and async tooling."""

from __future__ import annotations


def to_sqlalchemy_sync_url(database_url: str) -> str:
    """Convert a plain PostgreSQL DSN to SQLAlchemy's psycopg driver URL."""

    if database_url.startswith("postgresql+"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def to_sqlalchemy_async_url(database_url: str) -> str:
    """Convert a plain PostgreSQL DSN to SQLAlchemy's asyncpg driver URL."""

    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql+"):
        return database_url.replace("postgresql+", "postgresql+asyncpg+", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url
