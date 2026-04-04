"""Persistence adapters for MVP backend flows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from maintenance_backend.database import PostgresDatabase
from maintenance_backend.exceptions import EquipmentNotFound, IdempotencyConflict
from maintenance_backend.models import Equipment, EquipmentStateRecord, SystemActor
from maintenance_backend.schemas.common import UserRole
from maintenance_backend.schemas.common import StateRecordAuthor
from maintenance_backend.schemas.equipment_state_records import (
    EquipmentStateRecordCreateRequest,
    EquipmentStateRecordResponse,
)


class EquipmentRepository(Protocol):
    """Equipment reference lookup contract."""

    async def exists(self, equipment_id: str) -> bool: ...


class StateRecordRepository(Protocol):
    """State-record persistence contract."""

    async def create_or_get(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse: ...

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> EquipmentStateRecordResponse | None: ...


@dataclass(slots=True)
class PostgresEquipmentRepository:
    """Equipment repository backed by SQLAlchemy."""

    database: PostgresDatabase

    async def exists(self, equipment_id: str) -> bool:
        async with self.database.session() as session:
            result = await session.execute(
                select(Equipment.equipment_id).where(
                    Equipment.equipment_id == equipment_id
                )
            )
            return result.scalar_one_or_none() is not None


@dataclass(slots=True)
class PostgresStateRecordRepository:
    """State-record repository with idempotency support over SQLAlchemy."""

    database: PostgresDatabase

    async def create_or_get(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse:
        payload_hash = self._build_payload_hash(request)
        try:
            async with self.database.session() as session:
                existing = await self._get_existing_by_idempotency_key(
                    session,
                    request.idempotency_key,
                )
                if existing is not None:
                    if existing.payload_hash != payload_hash:
                        raise IdempotencyConflict()
                    return self._model_to_response(existing)

                if not await self._equipment_exists(session, request.equipment_id):
                    raise EquipmentNotFound()

                actor = await self._get_or_create_actor(session, request.author)
                record = EquipmentStateRecord(
                    record_id=f"state-record-{uuid4().hex}",
                    equipment_id=request.equipment_id,
                    author_actor_id=actor.actor_id,
                    channel=request.channel.value,
                    status=request.status.value,
                    comment=request.comment,
                    observed_at=request.observed_at,
                    created_at=datetime.now(tz=UTC),
                    source_type="manual",
                    idempotency_key=request.idempotency_key,
                    payload_hash=payload_hash,
                )
                record.author = actor
                session.add(record)
                await session.flush()
                await session.commit()
                return self._model_to_response(record)
        except IntegrityError as exc:
            if request.idempotency_key is None or not self._is_unique_violation(exc):
                raise

            async with self.database.session() as session:
                existing = await self._get_existing_by_idempotency_key(
                    session,
                    request.idempotency_key,
                )
                if existing is None:
                    raise
                if existing.payload_hash != payload_hash:
                    raise IdempotencyConflict() from exc
                return self._model_to_response(existing)

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> EquipmentStateRecordResponse | None:
        async with self.database.session() as session:
            record = await self._get_existing_by_idempotency_key(
                session, idempotency_key
            )
            if record is None:
                return None
            return self._model_to_response(record)

    def _build_payload_hash(self, request: EquipmentStateRecordCreateRequest) -> str:
        payload = request.model_dump(mode="json", exclude={"idempotency_key"})
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(canonical.encode("utf-8")).hexdigest()

    async def _equipment_exists(
        self,
        session: AsyncSession,
        equipment_id: str,
    ) -> bool:
        result = await session.execute(
            select(Equipment.equipment_id).where(Equipment.equipment_id == equipment_id)
        )
        return result.scalar_one_or_none() is not None

    async def _get_existing_by_idempotency_key(
        self,
        session: AsyncSession,
        idempotency_key: str | None,
    ) -> EquipmentStateRecord | None:
        if idempotency_key is None:
            return None

        result = await session.execute(
            select(EquipmentStateRecord)
            .options(selectinload(EquipmentStateRecord.author))
            .where(EquipmentStateRecord.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def _get_or_create_actor(
        self,
        session: AsyncSession,
        author: StateRecordAuthor,
    ) -> SystemActor:
        result = await session.execute(
            select(SystemActor).where(SystemActor.external_id == author.external_id)
        )
        actor = result.scalar_one_or_none()
        if actor is not None:
            if author.display_name is not None:
                actor.display_name = author.display_name
            if author.role is not None:
                actor.role = author.role.value
            return actor

        actor = SystemActor(
            actor_id=f"actor-{uuid4().hex}",
            external_id=author.external_id,
            display_name=author.display_name,
            role=(author.role or UserRole.USER).value,
            activity_scope=None,
            is_active=True,
        )
        session.add(actor)
        await session.flush()
        return actor

    def _is_unique_violation(self, exc: Exception) -> bool:
        orig = getattr(exc, "orig", None)
        sqlstate = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
        return sqlstate == "23505"

    def _model_to_response(
        self,
        record: EquipmentStateRecord,
    ) -> EquipmentStateRecordResponse:
        author_role = None
        if record.author is not None and record.author.role is not None:
            author_role = record.author.role
        author = StateRecordAuthor(
            external_id=record.author.external_id,
            display_name=record.author.display_name,
            role=author_role,
        )
        return EquipmentStateRecordResponse(
            record_id=record.record_id,
            equipment_id=record.equipment_id,
            status=record.status,
            comment=record.comment,
            observed_at=record.observed_at,
            created_at=record.created_at,
            channel=record.channel,
            author=author,
        )
