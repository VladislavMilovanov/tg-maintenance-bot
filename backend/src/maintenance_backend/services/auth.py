"""Authentication service — token issuance and actor resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

import sqlalchemy as sa

from maintenance_backend.database import PostgresDatabase
from maintenance_backend.db_schema import system_actors
from maintenance_backend.schemas.auth import LoginResponse, MeResponse


@dataclass
class AuthService:
    """Simple in-memory token store backed by the system_actors table."""

    database: PostgresDatabase
    token_store: dict[str, str] = field(default_factory=dict)

    async def login(self, telegram_username: str) -> LoginResponse:
        """Return (or create) a web actor for *telegram_username* and issue a token."""

        external_id = f"web:{telegram_username}"

        async with self.database.session() as session:
            result = await session.execute(
                sa.select(system_actors).where(
                    system_actors.c.external_id == external_id
                )
            )
            row = result.mappings().one_or_none()

            if row is None:
                actor_id = f"actor-{uuid4().hex}"
                await session.execute(
                    sa.insert(system_actors).values(
                        actor_id=actor_id,
                        external_id=external_id,
                        display_name=telegram_username,
                        role="user",
                        activity_scope=None,
                        is_active=True,
                    )
                )
                await session.commit()
                display_name: str | None = telegram_username
                role = "user"
            else:
                actor_id = row["actor_id"]
                display_name = row["display_name"]
                role = row["role"]

        token = uuid4().hex
        self.token_store[token] = actor_id

        return LoginResponse(
            access_token=token,
            actor_id=actor_id,
            display_name=display_name,
            role=role,
        )

    async def get_current_actor(self, token: str) -> MeResponse | None:
        """Resolve a bearer token to an actor, or return None if invalid."""

        actor_id = self.token_store.get(token)
        if actor_id is None:
            return None

        async with self.database.session() as session:
            result = await session.execute(
                sa.select(system_actors).where(system_actors.c.actor_id == actor_id)
            )
            row = result.mappings().one_or_none()

        if row is None:
            return None

        return MeResponse(
            actor_id=row["actor_id"],
            external_id=row["external_id"],
            display_name=row["display_name"],
            role=row["role"],
            is_active=row["is_active"],
        )
