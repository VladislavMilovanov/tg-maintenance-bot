"""Ephemeral conversation ID tracking for assistant requests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import uuid4


class ConversationStore(Protocol):
    """Minimal contract for validating and issuing conversation IDs."""

    async def resolve(self, conversation_id: str | None) -> str: ...


@dataclass(slots=True)
class InMemoryConversationStore:
    """In-memory TTL store for active conversation IDs."""

    ttl_seconds: int
    _active: dict[str, datetime] = field(default_factory=dict)

    async def resolve(self, conversation_id: str | None) -> str:
        now = datetime.now(tz=UTC)
        self._evict_expired(now)
        if conversation_id and conversation_id in self._active:
            self._active[conversation_id] = now + timedelta(seconds=self.ttl_seconds)
            return conversation_id

        new_id = f"conv-{uuid4().hex}"
        self._active[new_id] = now + timedelta(seconds=self.ttl_seconds)
        return new_id

    def _evict_expired(self, now: datetime) -> None:
        expired = [key for key, expires_at in self._active.items() if expires_at <= now]
        for key in expired:
            self._active.pop(key, None)
