"""Persistence adapters for MVP backend flows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from maintenance_backend.exceptions import EquipmentNotFound, IdempotencyConflict
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
    """Equipment repository backed by PostgreSQL."""

    database: object

    async def exists(self, equipment_id: str) -> bool:
        row = await self.database.pool.fetchrow(
            "SELECT equipment_id FROM equipment WHERE equipment_id = $1",
            equipment_id,
        )
        return row is not None


@dataclass(slots=True)
class PostgresStateRecordRepository:
    """State-record repository with idempotency support."""

    database: object

    async def create_or_get(
        self,
        request: EquipmentStateRecordCreateRequest,
    ) -> EquipmentStateRecordResponse:
        payload_hash = self._build_payload_hash(request)
        if request.idempotency_key is not None:
            existing = await self._fetch_row_by_idempotency_key(request.idempotency_key)
            if existing is not None:
                if existing["payload_hash"] != payload_hash:
                    raise IdempotencyConflict()
                return self._row_to_response(existing)

        if not await self._equipment_exists(request.equipment_id):
            raise EquipmentNotFound()

        record = EquipmentStateRecordResponse(
            record_id=f"state-record-{uuid4().hex}",
            equipment_id=request.equipment_id,
            status=request.status,
            comment=request.comment,
            observed_at=request.observed_at,
            created_at=datetime.now(tz=UTC),
            channel=request.channel,
            author=request.author,
        )
        try:
            await self.database.pool.execute(
                """
                INSERT INTO equipment_state_records (
                    record_id,
                    equipment_id,
                    status,
                    comment,
                    observed_at,
                    created_at,
                    channel,
                    author_external_id,
                    author_display_name,
                    author_role,
                    idempotency_key,
                    payload_hash
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                record.record_id,
                record.equipment_id,
                record.status.value,
                record.comment,
                record.observed_at,
                record.created_at,
                record.channel.value,
                record.author.external_id,
                record.author.display_name,
                None if record.author.role is None else record.author.role.value,
                request.idempotency_key,
                payload_hash,
            )
            return record
        except Exception as exc:
            if request.idempotency_key is None or not self._is_unique_violation(exc):
                raise

            existing = await self._fetch_row_by_idempotency_key(request.idempotency_key)
            if existing is None:
                raise
            if existing["payload_hash"] != payload_hash:
                raise IdempotencyConflict() from exc
            return self._row_to_response(existing)

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> EquipmentStateRecordResponse | None:
        row = await self._fetch_row_by_idempotency_key(idempotency_key)
        if row is None:
            return None
        return self._row_to_response(row)

    def _build_payload_hash(self, request: EquipmentStateRecordCreateRequest) -> str:
        payload = request.model_dump(mode="json", exclude={"idempotency_key"})
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(canonical.encode("utf-8")).hexdigest()

    async def _equipment_exists(self, equipment_id: str) -> bool:
        row = await self.database.pool.fetchrow(
            "SELECT equipment_id FROM equipment WHERE equipment_id = $1",
            equipment_id,
        )
        return row is not None

    async def _fetch_row_by_idempotency_key(
        self, idempotency_key: str
    ) -> object | None:
        return await self.database.pool.fetchrow(
            """
            SELECT record_id, equipment_id, status, comment, observed_at, created_at,
                   channel, author_external_id, author_display_name, author_role,
                   idempotency_key, payload_hash
            FROM equipment_state_records
            WHERE idempotency_key = $1
            """,
            idempotency_key,
        )

    def _is_unique_violation(self, exc: Exception) -> bool:
        try:
            import asyncpg
        except ImportError:  # pragma: no cover - dependency should exist in runtime
            return False
        return isinstance(exc, asyncpg.exceptions.UniqueViolationError)

    def _row_to_response(self, row: object) -> EquipmentStateRecordResponse:
        author = StateRecordAuthor(
            external_id=row["author_external_id"],
            display_name=row["author_display_name"],
            role=row["author_role"],
        )
        return EquipmentStateRecordResponse(
            record_id=row["record_id"],
            equipment_id=row["equipment_id"],
            status=row["status"],
            comment=row["comment"],
            observed_at=row["observed_at"],
            created_at=row["created_at"],
            channel=row["channel"],
            author=author,
        )
