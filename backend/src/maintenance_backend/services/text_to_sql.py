"""Text-to-SQL service: converts natural language to SQL, executes, and summarizes."""

from __future__ import annotations

import logging
import re
from typing import Any, Protocol

import sqlalchemy as sa
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from maintenance_backend.schemas.text_to_sql import TextToSqlResponse

logger = logging.getLogger(__name__)

_MUTATION_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

_ROW_LIMIT = 100
_TIMEOUT_MS = 5000

_SCHEMA_CONTEXT = (
    "Database: PostgreSQL\nTables:\n\n"
    "system_actors (actor_id TEXT PK, external_id TEXT, display_name TEXT, "
    "role TEXT[admin|engineer|operator|user], is_active BOOLEAN, "
    "created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "locations (location_id TEXT PK, name TEXT, location_type TEXT, "
    "parent_location_id TEXT FK->locations, display_order INT, is_active BOOLEAN, "
    "created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "equipment (equipment_id TEXT PK, name TEXT, equipment_code TEXT UNIQUE, "
    "location_id TEXT FK->locations, owner_actor_id TEXT FK->system_actors, "
    "current_status TEXT[normal|warning|critical|unknown], "
    "maintenance_due_at TIMESTAMPTZ, maintenance_completed_at TIMESTAMPTZ, "
    "is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "data_sources (source_id TEXT PK, "
    "source_type TEXT[manual|external_monitoring|import|backend_derived], "
    "name TEXT, is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "sensors (sensor_id TEXT PK, equipment_id TEXT FK->equipment, name TEXT, "
    "sensor_type TEXT, data_source_id TEXT FK->data_sources, "
    "is_primary_for_state BOOLEAN, last_observed_at TIMESTAMPTZ, "
    "is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "sensor_groups (sensor_group_id TEXT PK, equipment_id TEXT FK->equipment, "
    "name TEXT, group_type TEXT, data_source_id TEXT FK->data_sources, "
    "is_used_for_state_assessment BOOLEAN, image_url TEXT, is_active BOOLEAN, "
    "created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n\n"
    "sensor_group_members (sensor_group_id TEXT FK->sensor_groups PK, "
    "sensor_id TEXT FK->sensors PK, created_at TIMESTAMPTZ)\n\n"
    "equipment_state_snapshots (snapshot_id TEXT PK, "
    "equipment_id TEXT FK->equipment, "
    "status TEXT[normal|warning|critical|unknown], severity TEXT, summary TEXT, "
    "observed_at TIMESTAMPTZ, effective_at TIMESTAMPTZ, "
    "data_source_id TEXT FK->data_sources, created_at TIMESTAMPTZ)\n\n"
    "equipment_state_records (record_id TEXT PK, equipment_id TEXT FK->equipment, "
    "author_actor_id TEXT FK->system_actors, channel TEXT[telegram|web], "
    "status TEXT[normal|warning|critical|unknown], comment TEXT, "
    "observed_at TIMESTAMPTZ, created_at TIMESTAMPTZ, source_type TEXT, "
    "review_status TEXT[pending|reviewed|resolved], "
    "reviewed_by_actor_id TEXT FK->system_actors, "
    "reviewed_at TIMESTAMPTZ, review_comment TEXT, "
    "idempotency_key TEXT UNIQUE, payload_hash TEXT)\n\n"
    "knowledge_items (knowledge_item_id TEXT PK, title TEXT, body TEXT, "
    "is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)\n"
)

_SQL_SYSTEM_PROMPT = (
    "You are a PostgreSQL expert. Given the database schema and a user question, "
    "generate a single read-only SQL SELECT query that answers the question.\n\n"
    "Rules:\n"
    "- Output ONLY the raw SQL query, nothing else (no markdown, no explanation)\n"
    "- Use only SELECT statements\n"
    "- Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE\n"
    "- Always include LIMIT 100 unless doing a COUNT or single-value aggregate\n"
    "- Use proper PostgreSQL syntax\n"
    "- Reference only tables and columns defined in the schema below\n\n"
    f"Schema:\n{_SCHEMA_CONTEXT}"
)

_SUMMARIZE_SYSTEM_PROMPT = (
    "You are a helpful assistant for an equipment maintenance system. "
    "Given the user question, the SQL query, and the query results, "
    "write a concise natural-language answer (2-4 sentences). "
    "Be specific about numbers and names from the results. "
    "Answer in the same language as the question."
)


class TextToSqlGatewayError(Exception):
    """Raised when LLM gateway fails to produce SQL or summary."""


class TextToSqlGateway(Protocol):
    """LLM gateway contract for Text-to-SQL flow."""

    async def generate_sql(self, question: str) -> str: ...

    async def summarize_results(
        self,
        question: str,
        sql_query: str,
        columns: list[str],
        rows: list[list[Any]],
    ) -> str: ...

    async def close(self) -> None: ...


class OpenRouterTextToSqlGateway:
    """OpenAI-compatible gateway for the Text-to-SQL LLM calls."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = AsyncOpenAI(
            api_key=api_key or "missing",
            base_url=base_url,
            timeout=timeout_seconds,
        )

    async def generate_sql(self, question: str) -> str:
        if not self._api_key:
            raise TextToSqlGatewayError("OpenRouter API key is not configured.")
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SQL_SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
            )
        except Exception as exc:
            raise TextToSqlGatewayError("OpenRouter SQL generation failed.") from exc
        result = completion.choices[0].message.content if completion.choices else None
        if not isinstance(result, str) or not result.strip():
            raise TextToSqlGatewayError("OpenRouter returned empty SQL.")
        return result.strip()

    async def summarize_results(
        self,
        question: str,
        sql_query: str,
        columns: list[str],
        rows: list[list[Any]],
    ) -> str:
        if not self._api_key:
            raise TextToSqlGatewayError("OpenRouter API key is not configured.")
        table_lines = [" | ".join(str(c) for c in columns)]
        table_lines.append("-" * 60)
        for row in rows[:20]:
            table_lines.append(" | ".join(str(v) for v in row))
        table_str = "\n".join(table_lines)
        user_content = (
            f"Question: {question}\n\nSQL used:\n{sql_query}\n\n"
            f"Results ({len(rows)} row(s)):\n{table_str}"
        )
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SUMMARIZE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
            )
        except Exception as exc:
            raise TextToSqlGatewayError("OpenRouter summarization failed.") from exc
        result = completion.choices[0].message.content if completion.choices else None
        if not isinstance(result, str) or not result.strip():
            raise TextToSqlGatewayError("OpenRouter returned empty summary.")
        return result.strip()

    async def close(self) -> None:
        await self._client.close()


def validate_sql(sql: str) -> str:
    """Validate that SQL is a safe read-only SELECT statement.

    Returns the cleaned SQL, or raises ValueError with a human-readable reason.
    """
    cleaned = sql.strip().rstrip(";")
    first_keyword = cleaned.split()[0].upper() if cleaned.split() else ""
    if first_keyword != "SELECT":
        raise ValueError(f"Only SELECT statements are allowed. Got: {first_keyword!r}")
    match = _MUTATION_KEYWORDS.search(cleaned)
    if match:
        raise ValueError(f"Mutation keyword detected in query: {match.group()!r}")
    return cleaned


_SessionFactory = async_sessionmaker[AsyncSession]


class TextToSqlService:
    """Converts natural language questions to SQL, executes, and summarizes results."""

    def __init__(
        self,
        *,
        gateway: TextToSqlGateway,
        session_factory: _SessionFactory | None = None,
    ) -> None:
        self._gateway = gateway
        self._session_factory = session_factory

    async def answer_question(
        self,
        question: str,
        user_role: str = "user",
    ) -> TextToSqlResponse:
        """Run the full Text-to-SQL pipeline for the given question."""
        try:
            raw_sql = await self._gateway.generate_sql(question)
        except TextToSqlGatewayError as exc:
            logger.warning("SQL generation failed: %s", exc)
            return TextToSqlResponse(
                answer=(
                    "Не удалось сгенерировать SQL-запрос. "
                    "Попробуйте переформулировать вопрос."
                ),
                error=str(exc),
            )

        try:
            safe_sql = validate_sql(raw_sql)
        except ValueError as exc:
            logger.warning("SQL validation rejected query: %s | SQL: %s", exc, raw_sql)
            return TextToSqlResponse(
                answer="Запрос отклонён по соображениям безопасности.",
                sql_query=raw_sql,
                error=str(exc),
            )

        try:
            columns, rows = await self._execute_sql(safe_sql)
        except Exception as exc:
            logger.warning("SQL execution failed: %s | SQL: %s", exc, safe_sql)
            return TextToSqlResponse(
                answer=(
                    "Ошибка при выполнении запроса. Возможно, вопрос требует уточнения."
                ),
                sql_query=safe_sql,
                error=str(exc),
            )

        try:
            answer = await self._gateway.summarize_results(
                question, safe_sql, columns, rows
            )
        except TextToSqlGatewayError as exc:
            logger.warning("Result summarization failed: %s", exc)
            answer = (
                f"Запрос вернул {len(rows)} строк(и). Столбцы: {', '.join(columns)}."
            )

        return TextToSqlResponse(
            answer=answer,
            sql_query=safe_sql,
            row_count=len(rows),
            columns=columns,
            rows=rows,
        )

    async def _execute_sql(
        self,
        sql: str,
    ) -> tuple[list[str], list[list[Any]]]:
        """Execute a validated SELECT statement and return (columns, rows)."""
        factory = self._session_factory
        if factory is None:
            raise RuntimeError("No database session factory configured.")
        async with factory() as session:
            await session.execute(
                sa.text(f"SET LOCAL statement_timeout = '{_TIMEOUT_MS}'")
            )
            limited_sql = self._apply_row_limit(sql)
            result = await session.execute(sa.text(limited_sql))
            db_rows = result.fetchall()
            columns = list(result.keys())
            rows = [list(row) for row in db_rows]
            return columns, rows

    @staticmethod
    def _apply_row_limit(sql: str) -> str:
        """Append LIMIT clause if not already present in the query."""
        if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
            return sql
        return f"{sql} LIMIT {_ROW_LIMIT}"
