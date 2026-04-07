# Iteration 9: Text-to-SQL — Plan

## Goal

Enable users to ask arbitrary natural language questions about the equipment database and receive accurate, summarised answers backed by live SQL queries.

## Approach

An LLM-based Text-to-SQL pipeline with read-only safety guardrails was selected. Two alternative approaches were evaluated and rejected:

| Approach | Decision | Reason |
|---|---|---|
| Text-to-SQL (LLM generates SELECT) | **Accepted** | Full query flexibility, reuses existing OpenRouter LLM infra |
| RAG over DB (vector embeddings) | Rejected | Semantic similarity cannot express aggregations/joins |
| Hardcoded query templates | Rejected | Cannot cover open-ended analytical questions, brittle to schema changes |
| Hybrid (template + LLM fallback) | Rejected | Unnecessary complexity for MVP |

The decision is formalised in `docs/adr/adr-004-text-to-sql.md`.

## Architecture

### 4-Step Pipeline (`TextToSqlService.answer_question`)

```
User question (natural language)
        │
        ▼
[1] LLM generates SQL
    • System prompt embeds full DB schema (tables, columns, types)
    • Model instructed to output only a single SELECT statement
        │
        ▼
[2] SQL safety validation (validate_sql)
    • Only SELECT statements allowed (first keyword check)
    • Mutation blocklist regex: INSERT, UPDATE, DELETE, DROP,
      ALTER, TRUNCATE, CREATE, GRANT, REVOKE
        │
        ▼
[3] Execute against DB (read-only AsyncSession)
    • SET LOCAL statement_timeout = '5000'
    • LIMIT 100 enforced if not already present
        │
        ▼
[4] LLM summarises results in natural language
    • Receives: question + SQL + tabular results (up to 20 rows shown)
    • Returns concise human-readable answer in the question's language
        │
        ▼
[5] API response: answer + sql_query + columns + rows + row_count
```

## Backend Components

### Service: `TextToSqlService`

File: `backend/src/maintenance_backend/services/text_to_sql.py`

- `TextToSqlService.answer_question(question, user_role)` — full pipeline
- `validate_sql(sql) -> str` — safety validation, raises `ValueError` on rejection
- `OpenRouterTextToSqlGateway` — LLM adapter (implements `TextToSqlGateway` protocol)
- `TextToSqlGatewayError` — exception for LLM failures

### Endpoint: `POST /api/v1/query/text-to-sql`

File: `backend/src/maintenance_backend/api/v1/text_to_sql.py`

- Router prefix: `/query`, tag: `query`
- Auth: `Authorization: Bearer {token}` required
- Request: `TextToSqlRequest { question: str (min_length=1) }`
- Response: `TextToSqlResponse { answer, sql_query?, row_count, columns, rows, error? }`

## Frontend Components

### Types: `src/lib/api/types.ts`

```typescript
export interface TextToSqlRequest { question: string; }
export interface TextToSqlResponse {
  answer: string;
  sql_query?: string;
  row_count: number;
  columns: string[];
  rows: unknown[][];
  error?: string;
}
```

### Endpoint function: `src/lib/api/endpoints.ts`

```typescript
export async function queryTextToSql(data: TextToSqlRequest): Promise<TextToSqlResponse>
```

## Test Plan (15 tests in `backend/tests/test_text_to_sql_api.py`)

### API integration tests (5 scenarios)

1. Count critical equipment → returns `row_count=1`, `columns=["count"]`
2. Top-3 problematic equipment in last 7 days → returns 3 rows with name + issue_count
3. Percentage of equipment in normal condition → returns `pct_normal` column
4. Locations with equipment count → returns location_name + equipment_count
5. Mutation query (DELETE) → returns answer with error, `row_count=0`

### `validate_sql` unit tests (7)

6. Accepts valid SELECT
7. Strips trailing semicolon
8. Rejects DELETE
9. Rejects INSERT
10. Rejects mutation keyword inside SELECT (SQL injection: `SELECT …; DROP TABLE …`)
11. Rejects UPDATE
12. Rejects DROP

### Auth guard tests (3)

13. Unauthenticated request → 401
14. Invalid token → 401
15. Empty question string → 422

## Documentation Updates

- `docs/adr/adr-004-text-to-sql.md` — architecture decision record
- `docs/integrations.md` — Text-to-SQL section
- `backend/docs/api-contracts.md` — `POST /api/v1/query/text-to-sql` endpoint contract

## Artifacts

| File | Role |
|---|---|
| `docs/adr/adr-004-text-to-sql.md` | ADR |
| `backend/src/maintenance_backend/services/text_to_sql.py` | Service + gateway |
| `backend/src/maintenance_backend/api/v1/text_to_sql.py` | Endpoint |
| `backend/src/maintenance_backend/schemas/text_to_sql.py` | Request/response schemas |
| `frontend/src/lib/api/types.ts` | Frontend types |
| `frontend/src/lib/api/endpoints.ts` | Frontend API function |
| `backend/tests/test_text_to_sql_api.py` | 15 tests |
| `docs/integrations.md` | Updated |
| `backend/docs/api-contracts.md` | Updated |
